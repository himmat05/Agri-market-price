const API = import.meta.env.VITE_API_BASE_URL;

if (!API) {
  console.error("❌ VITE_API_BASE_URL is undefined");
}

export default API;
