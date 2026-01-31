import { API_BASE } from './config.js';

export function apiUrl(path) {
    return `${API_BASE}${path}`;
}
