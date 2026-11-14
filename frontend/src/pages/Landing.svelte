<script>
  import { ArrowRight, ArrowUpRight, Globe } from '@lucide/svelte';
  import FireMap from '../components/FireMap.svelte';
</script>

<section class="hero" aria-labelledby="hero-title">
  <img class="hero-image" src="{import.meta.env.BASE_URL}incendio-aereo.webp" alt="" fetchpriority="high" />
  <div class="hero-content">
    <p class="eyebrow"><span class="status-dot"></span> OBSERVATÓRIO DE INCÊNDIOS FLORESTAIS</p>
    <h1 id="hero-title">Incêndios sob<br />um novo <em>olhar.</em></h1>
    <p class="hero-description">Explore focos de incêndio em um mapa mundial e visualize como a atividade muda entre regiões.</p>
    <a href="#/painel" class="button button-primary">Explorar painel <ArrowRight size={18} /></a>
  </div>
  <span class="image-caption">Imagem ilustrativa</span>
</section>

<section class="landing-preview" aria-labelledby="preview-title">
  <div class="preview-copy">
    <p class="eyebrow"><Globe size={16} /> MAPA E ANÁLISES</p>
    <h2 id="preview-title">Do mundo à<br />sua região.</h2>
    <p>Explore o mapa e acompanhe a atividade com séries temporais, comparativos e uma visualização 3D.</p>
    <a class="text-link" href="#/painel">Conhecer as visualizações <ArrowUpRight size={17} /></a>
  </div>

  <a class="preview-map card" href="#/painel" aria-label="Abrir mapa demonstrativo no painel">
    <div class="preview-map-header"><span><Globe size={17} /> Mapa de focos</span><span class="demo-label">Dados simulados</span></div>
    <FireMap id="landing-map" />
  </a>
</section>
