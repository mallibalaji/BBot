// Safe UUID generator with fallback for non-secure contexts
function makeId() {
    try {
      if (window?.crypto?.randomUUID) return window.crypto.randomUUID();
    } catch (_) {}
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  // LocalStorage keys
  const LS_KEYS = { PRODUCTS: 'lp_products', ADMIN: 'lp_admin' };
  
  // Initialize defaults
  function initDefaults() {
    if (!localStorage.getItem(LS_KEYS.ADMIN)) {
      localStorage.setItem(LS_KEYS.ADMIN, JSON.stringify({ username: 'admin', password: 'lemon123' }));
    }
    if (!localStorage.getItem(LS_KEYS.PRODUCTS)) {
      const seed = [
        { id: makeId(), name: 'Classic Lemon Pickle', price: 199, description: 'Tangy traditional lemon pickle with home-ground spices.', image: 'https://picsum.photos/seed/lemon1/600/400', available: true },
        { id: makeId(), name: 'Sweet & Spicy Lemon', price: 229, description: 'Balanced sweet-heat profile for snack pairings.', image: 'https://picsum.photos/seed/lemon2/600/400', available: true },
        { id: makeId(), name: 'Garlic Lemon Pickle', price: 249, description: 'Bold garlic notes with zesty lemon chunks.', image: 'https://picsum.photos/seed/lemon3/600/400', available: false }
      ];
      localStorage.setItem(LS_KEYS.PRODUCTS, JSON.stringify(seed));
    }
  }
  
  // Product helpers
  function getProducts() { const raw = localStorage.getItem(LS_KEYS.PRODUCTS); return raw ? JSON.parse(raw) : []; }
  function saveProducts(list) { localStorage.setItem(LS_KEYS.PRODUCTS, JSON.stringify(list)); }
  function addProduct(p) { const list = getProducts(); list.push({ ...p, id: makeId() }); saveProducts(list); }
  function updateProduct(id, patch) { const list = getProducts(); const idx = list.findIndex(x => x.id === id); if (idx >= 0) { list[idx] = { ...list[idx], ...patch, id }; saveProducts(list); } }
  function deleteProduct(id) { const list = getProducts().filter(x => x.id !== id); saveProducts(list); }
  
  // Admin auth
  function getAdmin() { const raw = localStorage.getItem(LS_KEYS.ADMIN); return raw ? JSON.parse(raw) : null; }
  function verifyLogin(username, password) { const a = getAdmin(); return a && a.username === username && a.password === password; }
  function setAdmin(username, password) { localStorage.setItem(LS_KEYS.ADMIN, JSON.stringify({ username, password })); }
  
  // Expose global after definitions
  window.LemonStore = { initDefaults, getProducts, addProduct, updateProduct, deleteProduct, verifyLogin, setAdmin };
  