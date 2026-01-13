# 🔍 DIAGNÓSTICO LCP - Instruções

## 1. Abrir o Site e DevTools

1. Abra: http://72.61.36.89:8080
2. Pressione F12 (DevTools)
3. Vá para a aba "Console"
4. Recarregue a página (Ctrl+Shift+R para hard refresh)

## 2. Verificar Logs no Console

Você verá 3 grupos de logs:

### 🎯 LCP DEBUG
```
LCP Time: 3400 ms
LCP Element: <img> ou <h1> ou outro
Element Tag: IMG
Element Classes: ...
Image Source: /static/images/hero/logohome3-????w.avif (qual tamanho?)
```

**Anote:**
- Qual é o elemento LCP? (IMG, H1, DIV?)
- Se for IMG: qual formato está sendo carregado? (AVIF, WebP, PNG?)
- Se for IMG: qual largura? (640w, 960w, 1280w, 1920w, 2560w?)

### 🖼️ IMAGES LOADING
```
Image 0: { src: "/static/images/hero/...", naturalSize: "1920x1280", ... }
```

**Anote:**
- Qual imagem está marcada com fetchpriority="high"?
- Qual o tamanho natural da imagem carregada?

### ⚡ TIMING METRICS
```
TTFB: 150 ms
first-contentful-paint: 1200 ms
largest-contentful-paint: 3400 ms
```

**Anote:**
- TTFB (Time to First Byte)
- FCP vs LCP (diferença)

## 3. Verificar Network Tab

1. Vá para aba "Network"
2. Recarregue a página
3. Filtrar por "Img"
4. Encontre a imagem do hero (logohome3)

**Anote:**
- Formato: AVIF, WebP ou PNG?
- Tamanho do arquivo (Size): KB transferido
- Tempo de download (Time): ms
- Status code: 200, 304 (cached)?
- Response headers: content-type, cache-control

## 4. Verificar Preload

1. Na aba "Network", filtre por "All"
2. Veja se há um request para a imagem ANTES do HTML terminar de parsear
3. Verifique se há linha "Initiator: Preload" na imagem do hero

## 5. Lighthouse Local (Opcional mas Recomendado)

1. DevTools > aba "Lighthouse"
2. Selecione "Desktop"
3. Selecione apenas "Performance"
4. Click "Analyze page load"
5. Após análise, vá em "View Trace" e procure "Largest Contentful Paint"

**Captura:**
- Screenshot do elemento LCP destacado
- Métricas exatas

## 6. Reportar Achados

Depois de coletar os dados acima, me informe:

```
ELEMENTO LCP: <IMG> ou <H1> ou outro?
FORMATO CARREGADO: AVIF / WebP / PNG?
TAMANHO ARQUIVO: ?? KB
TEMPO DOWNLOAD: ?? ms
TTFB: ?? ms
FCP: ?? ms
LCP: ?? ms
PRELOAD FUNCIONANDO: SIM / NÃO
```

## 7. Possíveis Causas (analisar após coletar dados)

### Se LCP for IMG mas está em 3.4s:
- ❌ Preload não está funcionando (URL não bate)
- ❌ Imagem não está em AVIF (navegador não suporta? fallback para PNG?)
- ❌ Servidor lento (TTFB alto)
- ❌ CSS bloqueando render (preload+onload atrasando)
- ❌ Imagem muito grande (srcset escolhendo tamanho errado)

### Se LCP for H1 (texto):
- ❌ Fontes bloqueando render
- ❌ Critical CSS insuficiente
- ❌ Bootstrap CSS bloqueando (preload+onload falhou)
- ❌ Overlay/blur pesado no hero

### Se LCP for outro elemento:
- ❌ Hero img não está visível above-the-fold
- ❌ Stats bar ou outro elemento está maior que hero
- ❌ Layout shift empurrando hero para baixo

## 🚨 Próximo Passo

Colete os dados e me envie. Só assim posso identificar a causa EXATA e aplicar a correção específica sem assumir.
