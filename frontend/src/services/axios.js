/**
 * Axios API Client
 * ----------------
 * Centralized HTTP client for backend communication
 * Base URL points to local backend server
 */

import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:5000/api",
  timeout: 30000, // 30 seconds
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * REQUEST INTERCEPTOR
 * Logs outgoing requests and adds timestamp
 */
apiClient.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date() };

    console.log(
      `[API REQUEST] ${config.method?.toUpperCase()} ${config.url}`,
      config.params || config.data || ""
    );

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * RESPONSE INTERCEPTOR
 * Handles common HTTP errors and returns response.data
 */
apiClient.interceptors.response.use(
  (response) => {
    const duration =
      new Date() - response.config.metadata.startTime;

    console.log(
      `[API RESPONSE] ${response.config.url} (${duration}ms)`
    );

    return response.data;
  },
  (error) => {
    if (error.response) {
      const status = error.response.status;

      if (status === 400) {
        console.error("❌ Bad Request");
      } else if (status === 404) {
        console.error("❌ API Not Found");
      } else if (status >= 500) {
        console.error("❌ Server Error");
      }
    } else {
      console.error("❌ Network / Timeout Error");
    }

    return Promise.reject(error);
  }
);

export default apiClient;
