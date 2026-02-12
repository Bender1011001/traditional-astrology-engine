export const SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const DEFAULT_API_URL = "https://traditional-astrology.com";

if (!window.CAEL_API_BASE && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    window.CAEL_API_BASE = DEFAULT_API_URL;
}

export const API_BASE = window.CAEL_API_BASE || "";
