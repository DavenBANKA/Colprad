# Guide Responsive Design - COLPRAD

## Vue d'ensemble

Le site COLPRAD est entièrement responsive et optimisé pour tous les appareils :
- 📱 Mobile (< 768px)
- 📱 Tablette (768px - 991px)
- 💻 Desktop (> 992px)

## Breakpoints

```css
/* Mobile First */
Base: < 576px
Small: ≥ 576px
Medium: ≥ 768px
Large: ≥ 992px
XLarge: ≥ 1200px
```

## Optimisations Mobile

### 1. Navigation
- ✅ Menu hamburger avec animation
- ✅ Liens tactiles (min 44px)
- ✅ Fond semi-transparent avec blur
- ✅ Boutons pleine largeur

### 2. Typographie
- ✅ Tailles réduites pour mobile
- ✅ H1: 2rem (mobile) vs 3rem (desktop)
- ✅ Line-height optimisé
- ✅ Font-size 16px minimum (évite zoom iOS)

### 3. Boutons & Forms
- ✅ Boutons pleine largeur sur mobile
- ✅ Touch targets 44x44px minimum
- ✅ Input font-size 16px (évite zoom)
- ✅ Spacing optimisé

### 4. Tableaux
- ✅ Scroll horizontal avec momentum
- ✅ Colonnes masquées sur mobile
- ✅ Font-size réduit
- ✅ Padding optimisé

### 5. Cards
- ✅ Hover lift désactivé sur touch
- ✅ Padding réduit
- ✅ Margin optimisé
- ✅ Stack vertical

### 6. Images
- ✅ Max-width 100%
- ✅ Height auto
- ✅ Lazy loading
- ✅ Responsive images

## Classes Utilitaires

### Visibilité
```html
<!-- Masquer sur mobile -->
<div class="hide-mobile">...</div>

<!-- Afficher uniquement sur mobile -->
<div class="show-mobile d-none d-md-block">...</div>

<!-- Masquer sur desktop -->
<div class="d-md-none">...</div>
```

### Alignement
```html
<!-- Centrer sur mobile -->
<div class="text-mobile-center">...</div>

<!-- Gauche sur mobile -->
<div class="text-mobile-left">...</div>
```

### Spacing
```html
<!-- Padding réduit sur mobile -->
<div class="p-mobile-2">...</div>

<!-- Margin réduit sur mobile -->
<div class="m-mobile-2">...</div>
```

## Optimisations Tactiles

### Touch Targets
- Minimum 44x44px pour tous les éléments interactifs
- Espacement suffisant entre les éléments
- Pas de hover effects sur touch devices

### Gestures
- Swipe horizontal pour les tableaux
- Pull to refresh désactivé si nécessaire
- Pinch to zoom contrôlé

### Performance
- Transitions désactivées sur touch
- Animations réduites
- Scroll momentum natif

## Accessibilité

### Keyboard Navigation
- Focus visible
- Tab order logique
- Skip links

### Screen Readers
- ARIA labels
- Alt text sur images
- Semantic HTML

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
    /* Animations désactivées */
}
```

### High Contrast
```css
@media (prefers-contrast: high) {
    /* Contraste augmenté */
}
```

## Tests Recommandés

### Devices
- ✅ iPhone SE (375px)
- ✅ iPhone 12/13 (390px)
- ✅ iPhone 14 Pro Max (430px)
- ✅ iPad (768px)
- ✅ iPad Pro (1024px)
- ✅ Desktop (1920px)

### Browsers
- ✅ Safari iOS
- ✅ Chrome Android
- ✅ Chrome Desktop
- ✅ Firefox
- ✅ Edge

### Orientations
- ✅ Portrait
- ✅ Landscape

## Performance Mobile

### Optimisations
- Lazy loading images
- Minification CSS/JS
- Compression GZIP
- CDN pour assets
- Service Worker (PWA)

### Métriques Cibles
- First Contentful Paint: < 1.8s
- Time to Interactive: < 3.8s
- Cumulative Layout Shift: < 0.1
- Largest Contentful Paint: < 2.5s

## Checklist Responsive

- [ ] Navigation mobile fonctionnelle
- [ ] Tous les boutons tactiles (44px min)
- [ ] Formulaires utilisables sur mobile
- [ ] Tableaux scrollables
- [ ] Images responsive
- [ ] Texte lisible sans zoom
- [ ] Pas de scroll horizontal
- [ ] Touch targets espacés
- [ ] Performance optimale
- [ ] Tests sur vrais devices

## Maintenance

### Ajout de Nouvelles Pages
1. Utiliser les classes Bootstrap responsive
2. Tester sur mobile d'abord
3. Ajouter classes utilitaires si nécessaire
4. Vérifier touch targets
5. Tester sur vrais devices

### Debugging
```javascript
// Afficher la taille d'écran
console.log(window.innerWidth + 'x' + window.innerHeight);

// Détecter touch device
const isTouchDevice = 'ontouchstart' in window;
```

---

**Dernière mise à jour** : Janvier 2025
**Responsable** : Daven BANKA
