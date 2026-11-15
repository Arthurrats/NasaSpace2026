<script>
  import { onMount } from 'svelte';

  let { data: suppliedData = [], seriesLabel = 'Países', unit = 'focos' } = $props();
  let host = $state();
  let chart = $state();
  let chartError = $state(false);
  let hovered = $state();
  const data = $derived(suppliedData.filter(item => Number.isFinite(item.value)));
  const series = $derived([...new Set(data.map(item => item.series))]);
  const months = $derived([...new Set(data.map(item => item.month))].sort());
  const countryColors = ['#78c850', '#b6e36b', '#ff8a32', '#e84b32', '#64aa80', '#d1e98c', '#f5a34c', '#c85d43', '#398f6b', '#8bcf92', '#f06d46', '#a4bf5a'];

  $effect(() => chart?.update(data));

  onMount(() => {
    let active = true;
    async function initialize() {
      try {
        const THREE = await import('three');
        const { OrbitControls } = await import('three/addons/controls/OrbitControls.js');
        if (!active) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
        camera.position.set(15, 13, 17);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.setClearColor(0x000000, 0);
        host.appendChild(renderer.domElement);

        const css = getComputedStyle(host);
        const gridColor = new THREE.Color(css.getPropertyValue('--border-strong').trim() || '#45635b');
        const surfaceColor = new THREE.Color(css.getPropertyValue('--surface').trim() || '#1d302a');
        scene.add(new THREE.HemisphereLight(0xe7ffda, 0x12201d, 2.1));
        const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
        keyLight.position.set(-3, 9, 6);
        scene.add(keyLight);
        const ground = new THREE.GridHelper(18, 18, gridColor, gridColor);
        ground.position.y = -0.025;
        scene.add(ground);

        const bars = new THREE.Group();
        scene.add(bars);
        const geometry = new THREE.BoxGeometry(0.66, 1, 0.62);
        const materials = countryColors.map(color => new THREE.MeshStandardMaterial({
          color,
          roughness: 0.36,
          metalness: 0.12,
          emissive: surfaceColor,
          emissiveIntensity: 0.12,
        }));
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.target.set(0, 1.1, 0);
        controls.enablePan = false;
        controls.touches.TWO = THREE.TOUCH.DOLLY_ROTATE;
        controls.minDistance = 7;
        controls.maxDistance = 30;
        controls.maxPolarAngle = Math.PI * 0.48;
        controls.update();

        const raycaster = new THREE.Raycaster();
        const pointer = new THREE.Vector2();
        function render() { renderer.render(scene, camera); }
        controls.addEventListener('change', render);

        function updateBars(rows) {
          bars.clear();
          hovered = undefined;
          const peak = Math.max(1, ...rows.map(row => row.value));
          const seriesIndex = new Map(series.map((label, index) => [label, index]));
          const monthIndex = new Map(months.map((month, index) => [month, index]));
          for (const row of rows) {
            if (row.value <= 0) continue;
            const seriesPosition = seriesIndex.get(row.series) ?? 0;
            const monthPosition = monthIndex.get(row.month) ?? 0;
            const height = Math.max(0.025, row.value / peak * 5.2);
            const bar = new THREE.Mesh(geometry, materials[seriesPosition % materials.length]);
            bar.scale.y = height;
            bar.position.set((seriesPosition - (series.length - 1) / 2) * 1.05, height / 2, (monthPosition - (months.length - 1) / 2) * 0.92);
            bar.userData = row;
            bars.add(bar);
          }
          render();
        }

        function resize() {
          const { width, height } = host.getBoundingClientRect();
          if (!width || !height) return;
          camera.aspect = width / height;
          camera.updateProjectionMatrix();
          renderer.setSize(width, height, false);
          render();
        }
        const observer = new ResizeObserver(resize);
        observer.observe(host);
        resize();

        function movePointer(event) {
          const rect = renderer.domElement.getBoundingClientRect();
          pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
          pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
          raycaster.setFromCamera(pointer, camera);
          const hit = raycaster.intersectObjects(bars.children)[0]?.object;
          hovered = hit ? {
            series: hit.userData.series,
            month: hit.userData.month,
            value: hit.userData.value,
            x: Math.min(rect.width - 145, event.clientX - rect.left + 12),
            y: event.clientY - rect.top,
          } : undefined;
        }
        function leavePointer() { hovered = undefined; }
        renderer.domElement.addEventListener('pointermove', movePointer);
        renderer.domElement.addEventListener('pointerleave', leavePointer);

        chart = {
          update: updateBars,
          destroy() {
            observer.disconnect();
            renderer.domElement.removeEventListener('pointermove', movePointer);
            renderer.domElement.removeEventListener('pointerleave', leavePointer);
            controls.removeEventListener('change', render);
            controls.dispose();
            geometry.dispose();
            ground.dispose();
            materials.forEach(material => material.dispose());
            renderer.dispose();
            renderer.domElement.remove();
          },
        };
      } catch {
        if (active) chartError = true;
      }
    }
    initialize();
    return () => { active = false; chart?.destroy(); };
  });
</script>

<div class="three-chart" bind:this={host} role="img" aria-label="{unit} por {seriesLabel.toLowerCase()} e mês, em 3D">
  {#if chartError}<p class="empty-state">A visualização 3D não está disponível neste navegador.</p>{/if}
  {#if hovered}<div class="chart-tooltip" style:left={Math.max(4, hovered.x) + 'px'} style:top={Math.max(4, hovered.y - 10) + 'px'}><span>{hovered.series} · {hovered.month}</span><strong>{hovered.value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} {unit}</strong></div>{/if}
</div>
<div class="chart-axes">
  <div><small>{seriesLabel}</small><ul class="chart-labels" aria-label={seriesLabel}>
    {#each series as label, index (label)}
      <li><span style:background={countryColors[index % countryColors.length]}></span><strong>{label}</strong></li>
    {/each}
  </ul></div>
  <div><small>Meses</small><ol class="month-labels">
    {#each months as month (month)}
      <li>{new Date(month + '-02T00:00:00Z').toLocaleDateString('pt-BR', { month: 'short', timeZone: 'UTC' }).replace('.', '')}</li>
    {/each}
  </ol></div>
</div>

<style>
  .three-chart { position: relative; width: 100%; height: clamp(175px, 23vw, 235px); overflow: hidden; border-radius: var(--card-radius); background: radial-gradient(ellipse at 50% 85%, var(--accent-surface), transparent 70%); }
  .three-chart :global(canvas) { display: block; width: 100%; height: 100%; outline: none; }
  .chart-tooltip { position: absolute; z-index: 2; display: grid; gap: 3px; pointer-events: none; padding: 9px 11px; border: 1px solid var(--accent-border); border-radius: var(--control-radius); background: var(--surface-raised); color: var(--muted); font-size: .74rem; box-shadow: 0 8px 24px #0003; }
  .chart-tooltip strong { color: var(--text); font-size: .9rem; }
  .chart-axes { display: grid; gap: 6px; padding: 2px 12px 6px; }
  .chart-axes small { color: var(--muted); font-size: .62rem; font-weight: 700; letter-spacing: .1em; }
  .chart-labels { display: flex; flex-wrap: wrap; gap: 7px 12px; margin: 4px 0 0; padding: 0; list-style: none; }
  .chart-labels li { display: inline-flex; align-items: center; gap: 6px; color: var(--text); font-size: .7rem; }
  .chart-labels li span { width: 8px; height: 8px; border-radius: 50%; }
  .chart-labels li strong { font-weight: 550; }
  .month-labels { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 3px; margin: 4px 0 0; padding: 0; list-style: none; color: var(--muted); font-size: .67rem; text-align: center; text-transform: capitalize; }
</style>
