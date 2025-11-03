# Assets - Logo e Icone

Questa cartella contiene tutti i materiali grafici del progetto organizzati secondo uno standard riutilizzabile.

## Struttura Standard

```
assets/
├── logo/           # Loghi completi (con e senza testo)
├── icons/          # Icone in varie dimensioni
├── favicon/        # Favicon per web
└── README.md       # Questo file
```

## Nomenclatura File

### Logo
- **Con testo** (es. logo con scritta "gtext"):
  - `logo-with-text.png` - PNG con sfondo trasparente
  - `logo-with-text.svg` - SVG vettoriale

- **Senza testo** (solo icona/simbolo):
  - `logo-no-text.png` - PNG con sfondo trasparente
  - `logo-no-text.svg` - SVG vettoriale

### Icone
Icone quadrate senza testo in varie dimensioni:
- `icon-16x16.png`
- `icon-32x32.png`
- `icon-48x48.png`
- `icon-64x64.png`
- `icon-128x128.png`
- `icon-256x256.png`
- `icon-512x512.png`

### Favicon
Per uso web:
- `favicon.ico` - Multi-size ICO (16x16, 32x32, 48x48)
- `favicon-16x16.png`
- `favicon-32x32.png`

## Requisiti Tecnici

### Trasparenza
- ✅ Tutti i file PNG e SVG devono avere **sfondo trasparente**
- ✅ Usare canale alpha per PNG
- ✅ Nessun background nei file SVG

### Formati
- **PNG**: Per uso generico, web, documentazione
  - Compressione: Ottimizzata (PNG-8 o PNG-24 con alpha)
  - Risoluzione: 72 DPI per web, 300 DPI per print

- **SVG**: Per scalabilità e uso vettoriale
  - Ottimizzato (rimuovere metadata inutili)
  - Percorsi puliti (evitare trasformazioni complesse)

### Dimensioni Consigliate
- **Logo principale**: 512x512px o superiore (PNG)
- **Icone**: Multiple dimensioni (16px - 512px)
- **Favicon**: 16x16, 32x32, 48x48

## Uso nei Progetti

### Documentazione (MkDocs/Sphinx)
```yaml
# mkdocs.yml
theme:
  logo: assets/logo/logo-no-text.png
  favicon: assets/favicon/favicon.ico
```

### README.md
```markdown
<img src="assets/logo/logo-with-text.png" alt="Project Logo" width="200">
```

### Web/HTML
```html
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon/favicon-16x16.png">
```

## Note per Designer

Quando crei nuovi asset:
1. **Esporta sempre con sfondo trasparente**
2. **Fornisci sia PNG che SVG**
3. **Ottimizza i file** (usa tools come `optipng`, `svgo`)
4. **Testa su sfondo chiaro e scuro**
5. **Mantieni proporzioni 1:1 per icone**

## Tools Utili

- **PNG optimization**: `optipng`, `pngquant`
- **SVG optimization**: `svgo`
- **Favicon generation**: `favicon-generator`
- **Conversion**: `ImageMagick`, `inkscape`

## Standard per Altri Progetti

Questa struttura è **standard per tutti i progetti Genropy**.
Quando crei un nuovo progetto:
1. Copia questa struttura di cartelle
2. Sostituisci i file con i loghi del nuovo progetto
3. Mantieni la stessa nomenclatura
4. Aggiorna riferimenti in mkdocs.yml, README.md, etc.

---

**Ultimo aggiornamento**: 2025-11-03
**Versione**: 1.0.0
