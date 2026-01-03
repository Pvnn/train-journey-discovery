<template>
  <form class="search-form" @submit.prevent="submit">
    <!-- FROM / TO -->
    <div class="field-row">
      <div class="field">
        <label>From</label>
        <input
          v-model="origin"
          type="text"
          placeholder="City or station"
          required
        />
      </div>

      <button type="button" class="swap" @click="swap">⇄</button>

      <div class="field">
        <label>To</label>
        <input
          v-model="destination"
          type="text"
          placeholder="City or station"
          required
        />
      </div>
    </div>

    <!-- DATE / TIME -->
    <div class="field-row">
      <div class="field">
        <label>Date</label>
        <input v-model="date" type="date" required />
      </div>

      <div class="field">
        <label>Time</label>
        <input v-model="time" type="time" />
      </div>
    </div>

    <!-- CTA -->
    <button class="submit-btn" type="submit">
      Search train journeys
    </button>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const origin = ref("");
const destination = ref("");
const date = ref("");
const time = ref("");

const swap = () => {
  [origin.value, destination.value] = [
    destination.value,
    origin.value,
  ];
};

const submit = () => {
  router.push({
    path: "/results",
    query: {
      origin: origin.value,
      destination: destination.value,
      date: date.value,
      time: time.value,
    },
  });
};
</script>

<style scoped>
.search-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

/* ROW */
.field-row {
  display: flex;
  gap: 0.8rem;
  align-items: flex-end;
}

/* FIELD */
.field {
  flex: 1;
  display: flex;
  flex-direction: column;
}

label {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.3rem;
}

input {
  padding: 0.7rem 0.8rem;
  border-radius: 10px;
  border: 1px solid #ddd;
  font-size: 0.95rem;
}

input:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.15);
}

/* SWAP */
.swap {
  border: none;
  background: #eef3ff;
  border-radius: 50%;
  width: 42px;
  height: 42px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.swap:hover {
  transform: rotate(180deg);
}

/* BUTTON */
.submit-btn {
  margin-top: 0.6rem;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.85rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(0, 102, 204, 0.3);
}
</style>
