<template>
  <div class="search-container">
    <form class="search-card" @submit.prevent="handleSearch">
      <h2>Search Train Journeys</h2>

      <div class="row">
        <input v-model="origin" type="text" placeholder="Origin Station" />
        <button type="button" class="swap" @click="swapStations">⇄</button>
        <input
          v-model="destination"
          type="text"
          placeholder="Destination Station"
        />
      </div>

      <input v-model="date" type="date" />
      <input v-model="time" type="time" />

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit" class="search-btn">Search</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";

const origin = ref("");
const destination = ref("");
const date = ref("");
const time = ref("");
const error = ref("");

const emit = defineEmits(["search"]);

function swapStations() {
  [origin.value, destination.value] = [
    destination.value,
    origin.value,
  ];
}

function handleSearch() {
  error.value = "";

  if (!origin.value || !destination.value || !date.value) {
    error.value = "All fields are required";
    return;
  }

  if (origin.value === destination.value) {
    error.value = "Origin and destination cannot be same";
    return;
  }

  const today = new Date().toISOString().split("T")[0];
  if (date.value < today) {
    error.value = "Journey date cannot be in the past";
    return;
  }

  emit("search", {
    origin: origin.value,
    destination: destination.value,
    date: date.value,
    time: time.value,
  });
}
</script>

<style scoped>
.search-container {
  display: flex;
  justify-content: center;
  margin-top: 3rem;
}

.search-card {
  background: white;
  padding: 1.5rem;
  width: 360px;
  border-radius: 12px;
  border: 2px solid #0066cc;
}

h2 {
  color: #0066cc;
  margin-bottom: 1rem;
  text-align: center;
}

input {
  width: 100%;
  margin-bottom: 0.75rem;
}

.row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.swap {
  background: #ff9933;
  border: none;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
}

.search-btn {
  background: #0066cc;
  color: white;
  width: 100%;
  padding: 0.6rem;
  border-radius: 8px;
  border: none;
  margin-top: 0.5rem;
}

.error {
  color: red;
  font-size: 0.85rem;
}
</style>
