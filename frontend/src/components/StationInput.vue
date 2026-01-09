<template>
  <div class="station-input">
    <label>
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>

    <div
      class="input-wrapper"
      :class="{
        valid: isValid,
        invalid: isInvalid
      }"
    >
      <input
        type="text"
        v-model="query"
        :placeholder="placeholder"
        @focus="open = true"
        @blur="closeDropdown"
      />

      <button
        v-if="modelValue"
        class="clear-btn"
        @mousedown.prevent="clear"
        type="button"
      >
        ✕
      </button>
    </div>

    <!-- Dropdown -->
    <ul v-if="open && filteredStations.length" class="dropdown">
      <li
        v-for="station in filteredStations"
        :key="station.stop_id"
        @mousedown.prevent="selectStation(station)"
      >
        <strong>{{ station.stop_name }}</strong>
        <span class="code">({{ station.stop_code }})</span>
        <span class="zone"> - {{ station.zone }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";

/* props */
const props = defineProps({
  modelValue: {
    type: Object,
    default: null,
  },
  label: {
    type: String,
    default: "",
  },
  placeholder: {
    type: String,
    default: "Search station",
  },
  required: {
    type: Boolean,
    default: false,
  },
});

/* emits */
const emit = defineEmits(["update:modelValue"]);

/* state */
const query = ref("");
const debouncedQuery = ref("");
const open = ref(false);
const stations = ref([]);

/* load stops.json */
onMounted(async () => {
  const res = await fetch("/stops.json");
  const data = await res.json();
  stations.value = Array.isArray(data) ? data : Object.values(data);
});

/* sync input with selected station */
watch(
  () => props.modelValue,
  (val) => {
    query.value = val
      ? `${val.stop_name} (${val.stop_code})`
      : "";
  },
  { immediate: true }
);

/* debounce input */
let debounceTimer;
watch(query, (val) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    debouncedQuery.value = val.trim().toLowerCase();
    open.value = true;
  }, 300);
});

/* 🔒 LOCKED RANKING LOGIC — DO NOT CHANGE */
const filteredStations = computed(() => {
  if (!debouncedQuery.value) return [];

  const q = debouncedQuery.value;

  return stations.value
    .map((s) => {
      const name = s.stop_name.toLowerCase();
      const code = s.stop_code.toLowerCase();
      let score = 0;

      // 🔒 PERMANENT PRIORITY ORDER
      if (name.startsWith(q)) score = 3;
      else if (code.startsWith(q)) score = 2;
      else if (name.includes(q)) score = 1;

      return score > 0 ? { ...s, score } : null;
    })
    .filter(Boolean)
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return a.stop_name.length - b.stop_name.length;
    })
    .slice(0, 10);
});

/* validation state */
const isValid = computed(() => props.required && !!props.modelValue);
const isInvalid = computed(() => props.required && !props.modelValue);

/* actions */
const selectStation = (station) => {
  emit("update:modelValue", {
    stop_id: station.stop_id,
    stop_code: station.stop_code,
    stop_name: station.stop_name,
  });
  open.value = false;
};

const clear = () => {
  emit("update:modelValue", null);
  query.value = "";
};

const closeDropdown = () => {
  setTimeout(() => {
    open.value = false;
  }, 150);
};
</script>

<style scoped>
.station-input {
  position: relative;
  display: flex;
  flex-direction: column;
}

label {
  font-size: 0.75rem;
  color: #555;
  margin-bottom: 0.3rem;
}

.required {
  color: #cc0000;
}

/* INPUT */
.input-wrapper {
  position: relative;
}

input {
  width: 100%;
  padding: 0.7rem 2rem 0.7rem 0.8rem;
  border-radius: 10px;
  border: 2px solid #ddd;
  font-size: 0.95rem;
}

/* 🔴 INVALID */
.input-wrapper.invalid input {
  border-color: #e74c3c;
  box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.3);
}

/* 🟢 VALID */
.input-wrapper.valid input {
  border-color: #2ecc71;
  box-shadow: 0 0 0 2px rgba(46, 204, 113, 0.3);
}

input:focus {
  outline: none;
}

/* CLEAR BUTTON */
.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #cc0000;
}

/* DROPDOWN */
.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 10px;
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
  max-height: 260px;
  overflow-y: auto;
  z-index: 50;
  margin-top: 4px;
}

.dropdown li {
  padding: 0.6rem 0.8rem;
  cursor: pointer;
}

.dropdown li:hover {
  background: #f0f6ff;
}

.code {
  color: #0066cc;
  font-size: 0.8rem;
  margin-left: 0.3rem;
}

.zone {
  color: #777;
  font-size: 0.75rem;
}
</style>
