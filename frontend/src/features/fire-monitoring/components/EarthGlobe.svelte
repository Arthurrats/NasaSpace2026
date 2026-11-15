<script>
  import { onMount } from 'svelte';

  let { cells, metric, strongest } = $props();
  let host = $state();
  let updateTexture = $state();
  let unavailable = $state(false);
  const gridColumns = 1440;
  const gridRows = 720;
  const columnLimit = 750;

  $effect(() => updateTexture?.(cells, metric, strongest));

  function loadEarthImage() {
    const image = new Image();
    image.src = import.meta.env.BASE_URL + 'earth-blue-marble.jpg';
    return image.decode().then(() => image);
  }

  onMount(() => {
    let active = true;
    let dispose;
    Promise.all([import('three'), import('three/addons/controls/OrbitControls.js'), loadEarthImage()])
      .then(([THREE, { OrbitControls }, image]) => {
        if (!active) return;
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.domElement.setAttribute('aria-hidden', 'true');
        host.appendChild(renderer.domElement);

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1.18, 1.18, 1.18, -1.18, 0.1, 20);
        // SphereGeometry starts at the antimeridian with negative X at u = 0.
        const longitude = Math.PI * (180 - 60) / 180;
        camera.position.set(-3 * Math.cos(longitude), -0.52, 3 * Math.sin(longitude));
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enablePan = false;
        controls.touches.TWO = THREE.TOUCH.DOLLY_ROTATE;
        controls.minZoom = 0.85;
        controls.maxZoom = 3.2;
        controls.update();

        const surface = document.createElement('canvas');
        surface.width = image.naturalWidth;
        surface.height = image.naturalHeight;
        const painter = surface.getContext('2d');
        const texture = new THREE.CanvasTexture(surface);
        texture.colorSpace = THREE.SRGBColorSpace;
        texture.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
        const geometry = new THREE.SphereGeometry(1, 64, 40);
        const material = new THREE.MeshStandardMaterial({ map: texture, roughness: 1 });
        scene.add(new THREE.Mesh(geometry, material));
        const columnGeometry = new THREE.BoxGeometry(1, 1, 1);
        const columnMaterial = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.58, depthWrite: false });
        const columns = new THREE.InstancedMesh(columnGeometry, columnMaterial, columnLimit);
        columns.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
        columns.frustumCulled = false;
        columns.count = 0;
        scene.add(columns);
        const transform = new THREE.Object3D();
        const normal = new THREE.Vector3();
        const up = new THREE.Vector3(0, 1, 0);
        const color = new THREE.Color();
        scene.add(new THREE.AmbientLight(0xffffff, 1.1));
        const light = new THREE.DirectionalLight(0xffffff, 1.8);
        light.position.set(2, 2, 4);
        scene.add(light);

        const render = () => renderer.render(scene, camera);
        const resize = () => {
          const { clientWidth: width, clientHeight: height } = host;
          if (!width || !height) return;
          const aspect = width / height;
          const vertical = Math.max(1.42, 1.42 / aspect);
          camera.left = -vertical * aspect;
          camera.right = vertical * aspect;
          camera.top = vertical;
          camera.bottom = -vertical;
          camera.updateProjectionMatrix();
          renderer.setSize(width, height, false);
          render();
        };
        const observer = new ResizeObserver(resize);
        observer.observe(host);
        controls.addEventListener('change', render);
        resize();

        updateTexture = (rows, valueColumn, strongestIds) => {
          painter.globalAlpha = 1;
          painter.drawImage(image, 0, 0);
          let peak = 1;
          for (const cell of rows) peak = Math.max(peak, cell[valueColumn]);
          const normalizer = Math.log1p(peak);
          const width = surface.width / gridColumns;
          const height = surface.height / gridRows;
          for (const cell of rows) {
            if (cell[valueColumn] <= 0) continue;
            const strength = Math.log1p(cell[valueColumn]) / normalizer;
            painter.fillStyle = strength > .8 ? '#ed4934' : strength > .5 ? '#ff9041' : '#b6e36b';
            painter.globalAlpha = .45 + .55 * strength;
            painter.fillRect((cell[0] % gridColumns) * width, Math.floor(cell[0] / gridColumns) * height, width, height);
          }
          painter.globalAlpha = 1;
          texture.needsUpdate = true;

          const cellById = new Map(rows.map(cell => [cell[0], cell]));
          const strongest = strongestIds.map(id => cellById.get(id)).filter(Boolean);
          strongest.forEach((cell, index) => {
            const id = cell[0];
            const azimuth = ((id % gridColumns) + 0.5) / gridColumns * Math.PI * 2;
            const polar = (Math.floor(id / gridColumns) + 0.5) / gridRows * Math.PI;
            normal.set(-Math.cos(azimuth) * Math.sin(polar), Math.cos(polar), Math.sin(azimuth) * Math.sin(polar));
            const relative = cell[valueColumn] / peak;
            const altitude = 0.014 + 0.38 * Math.sqrt(relative);
            transform.position.copy(normal).multiplyScalar(1 + altitude / 2);
            transform.quaternion.setFromUnitVectors(up, normal);
            transform.scale.set(0.0045, altitude, 0.0045);
            transform.updateMatrix();
            columns.setMatrixAt(index, transform.matrix);
            color.set(relative >= 0.6 ? '#ff6650' : relative >= 0.22 ? '#ff9a4a' : '#b6e36b');
            columns.setColorAt(index, color);
          });
          columns.count = strongest.length;
          columns.instanceMatrix.needsUpdate = true;
          if (columns.instanceColor) columns.instanceColor.needsUpdate = true;
          render();
        };

        dispose = () => {
          observer.disconnect();
          controls.removeEventListener('change', render);
          controls.dispose();
          geometry.dispose();
          material.dispose();
          columns.dispose();
          columnGeometry.dispose();
          columnMaterial.dispose();
          texture.dispose();
          renderer.dispose();
          renderer.domElement.remove();
        };
      }).catch(() => { if (active) unavailable = true; });
    return () => { active = false; dispose?.(); };
  });
</script>

<div class="globe" bind:this={host} role="img" aria-label="Globo tridimensional com colunas perpendiculares à superfície nas células de maior atividade">
  {#if unavailable}<p>Globo 3D indisponível neste navegador.</p>{/if}
</div>

<style>
  .globe { width: 100%; height: clamp(265px, 31vw, 390px); background: radial-gradient(ellipse, var(--accent-surface), transparent 68%); }
  .globe :global(canvas) { display: block; width: 100%; height: 100%; }
  .globe p { padding: 16px; font-size: .8rem; color: var(--muted); }
</style>
