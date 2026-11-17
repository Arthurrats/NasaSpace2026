<script>
  import { onMount } from 'svelte';
  import Skeleton from '../../../components/Skeleton.svelte';

  let { rows, selected } = $props();
  let host = $state();
  let draw = $state();
  let unavailable = $state(false);

  $effect(() => draw?.(rows, selected));

  onMount(() => {
    let active = true;
    let dispose;

    Promise.all([import('three'), import('three/addons/controls/OrbitControls.js')]).then(([THREE, { OrbitControls }]) => {
      if (!active) return;
      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.domElement.setAttribute('aria-hidden', 'true');
      host.appendChild(renderer.domElement);
      const scene = new THREE.Scene();
      const camera = new THREE.OrthographicCamera(-5, 5, 4, -4, 0.1, 60);
      camera.position.set(4, 8, 11);
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enablePan = false;
      controls.touches.TWO = THREE.TOUCH.DOLLY_ROTATE;
      controls.minZoom = 0.65;
      controls.maxZoom = 2.4;
      controls.maxPolarAngle = Math.PI * 0.47;
      controls.update();

      scene.add(new THREE.HemisphereLight(0xffffff, 0x375248, 2));
      const light = new THREE.DirectionalLight(0xffffff, 2.2);
      light.position.set(-3, 6, 4);
      scene.add(light);

      const base = new THREE.BoxGeometry(1.9, 0.12, 1.9);
      const bubble = new THREE.SphereGeometry(1, 24, 16);
      const baseMaterial = new THREE.MeshStandardMaterial({ color: '#1d302a', roughness: 0.85 });
      const activeMaterial = new THREE.MeshStandardMaterial({ color: '#78c850', roughness: 0.85 });
      const palette = ['#b6e36b', '#78c850', '#ff8a32', '#e84b32'].map(color =>
        new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.08 })
      );
      const tiles = Array.from({ length: 9 }, (_, sector) => {
        const x = (sector % 3 - 1) * 2;
        const z = (Math.floor(sector / 3) - 1) * 2;
        const tile = new THREE.Mesh(base, baseMaterial);
        const sphere = new THREE.Mesh(bubble, palette[0]);
        tile.position.set(x, 0, z);
        sphere.position.set(x, 0, z);
        scene.add(tile, sphere);
        return { tile, sphere };
      });

      function render() { renderer.render(scene, camera); }
      function resize() {
        const { clientWidth: width, clientHeight: height } = host;
        if (!width || !height) return;
        const aspect = width / height;
        const halfHeight = Math.max(3.7, 3.8 / aspect);
        camera.top = halfHeight;
        camera.bottom = -halfHeight;
        camera.left = -halfHeight * aspect;
        camera.right = halfHeight * aspect;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height, false);
        render();
      }
      const observer = new ResizeObserver(resize);
      observer.observe(host);
      controls.addEventListener('change', render);
      resize();

      draw = (values, selection) => {
        const max = Math.max(0, ...values.map(row => row.value ?? 0));
        tiles.forEach(({ tile, sphere }, index) => {
          const value = values[index]?.value;
          const share = max && value > 0 ? value / max : 0;
          tile.material = String(index) === selection ? activeMaterial : baseMaterial;
          sphere.visible = share > 0;
          const radius = 0.88 * Math.cbrt(share);
          sphere.scale.setScalar(radius);
          sphere.position.y = 0.06 + radius;
          sphere.material = palette[Math.min(3, Math.floor(share * 4))];
        });
        render();
      };
      dispose = () => {
        observer.disconnect();
        controls.removeEventListener('change', render);
        controls.dispose();
        [base, bubble, baseMaterial, activeMaterial, ...palette].forEach(resource => resource.dispose());
        renderer.dispose();
        renderer.domElement.remove();
      };
    }).catch(() => { if (active) unavailable = true; });

    return () => { active = false; dispose?.(); };
  });
</script>

<div class="scene" bind:this={host} role="img" aria-label="Nove setores geográficos em 3D. O volume de cada bolha representa o valor da métrica." aria-busy={!draw && !unavailable}>
  {#if unavailable}<p>3D indisponível neste navegador. Consulte os valores por setor ao lado.</p>{/if}
  {#if !draw && !unavailable}<Skeleton height="100%" overlay />{/if}
</div>

<style>
  .scene { position: relative; width: 100%; height: var(--chart-height); background: radial-gradient(ellipse, var(--accent-surface), transparent 72%); }
  .scene :global(canvas) { display: block; width: 100%; height: 100%; }
  p { padding: 14px; color: var(--muted); font-size: .8rem; }
</style>
