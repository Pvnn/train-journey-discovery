<template>
  <div class="journey-card">
    <!-- Header -->
    <div class="header">
      <div>
        <h3>{{ trainNumber }} – {{ trainName }}</h3>
        <span class="subtitle">
          {{ duration }} • {{ transfers }} transfer(s)
        </span>
      </div>

      <span class="class-badge" :class="classColor">
        {{ trainClass }}
      </span>
    </div>

    <!-- Timeline -->
    <div class="timeline">
      <div class="time-block">
        <span class="time">{{ departureTime }}</span>
        <span class="station">{{ departureStation }}</span>
      </div>

      <div class="line">
        <span class="dot"></span>
        <span class="rail"></span>
        <span class="dot"></span>
      </div>

      <div class="time-block">
        <span class="time">{{ arrivalTime }}</span>
        <span class="station">{{ arrivalStation }}</span>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <div class="price">
        ₹{{ fare }}
        <span class="comfort">Comfort {{ comfortScore }}/5</span>
      </div>

      <button class="details-btn" @click="viewDetails">
        View Details
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  trainNumber: String,
  trainName: String,
  departureStation: String,
  departureTime: String,
  arrivalStation: String,
  arrivalTime: String,
  duration: String,
  transfers: Number,
  fare: Number,
  trainClass: String,
  comfortScore: Number,
});

/* emit event */
const emit = defineEmits(["view-details"]);

const viewDetails = () => {
  emit("view-details", {
    trainNumber: props.trainNumber,
  });
};

/* class color coding */
const classColor = computed(() => {
  if (props.trainClass === "AC") return "ac";
  if (props.trainClass === "Sleeper") return "sleeper";
  return "general";
});
</script>

<style scoped>
/* Card */
.journey-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.journey-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.12);
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h3 {
  margin: 0;
  color: #0066cc;
}

.subtitle {
  font-size: 0.85rem;
  color: #666;
}

/* Timeline */
.timeline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 1.2rem 0;
}

.time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time {
  font-weight: bold;
}

.station {
  font-size: 0.85rem;
  color: #555;
}

.line {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rail {
  height: 2px;
  width: 100%;
  background: #ccc;
}

.dot {
  width: 10px;
  height: 10px;
  background: #0066cc;
  border-radius: 50%;
}

/* Footer */
.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 1.1rem;
  font-weight: bold;
}

.comfort {
  display: block;
  font-size: 0.75rem;
  color: #777;
}

.details-btn {
  background: #0066cc;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
}

/* Class badge */
.class-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 20px;
}

.ac {
  background: #0066cc;
  color: white;
}

.sleeper {
  background: #ff9933;
  color: white;
}

.general {
  background: #999;
  color: white;
}

/* Responsive */
@media (max-width: 600px) {
  .timeline {
    flex-direction: column;
    gap: 0.75rem;
  }

  .line {
    width: 100%;
  }

  .footer {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
}
</style>
