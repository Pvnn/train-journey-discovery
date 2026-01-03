<template>
  <div class="journey-card" @click="goToDetails">
    <!-- Header -->
    <div class="header">
      <div>
        <strong>{{ trainNumber }}</strong>
        <span class="train-name"> — {{ trainName }}</span>
      </div>

      <span class="class-badge" :class="trainClass.toLowerCase()">
        {{ trainClass }}
      </span>
    </div>

    <!-- Timeline -->
    <div class="timeline">
      <div class="station">
        <div class="time">{{ departureTime }}</div>
        <div class="code">{{ departureStation }}</div>
      </div>

      <div class="arrow">→</div>

      <div class="station">
        <div class="time">{{ arrivalTime }}</div>
        <div class="code">{{ arrivalStation }}</div>
      </div>
    </div>

    <!-- Meta -->
    <div class="meta">
      <span>⏱ {{ duration }}</span>
      <span>🔁 {{ transfers }} transfer(s)</span>
    </div>

    <!-- Footer -->
    <div class="footer">
      <div class="price">
        ₹{{ fare }}
        <div class="stars">
          <span
            v-for="i in 5"
            :key="i"
            :class="{ filled: i <= comfortScore }"
          >
            ★
          </span>
        </div>
      </div>

      <button class="view-btn" @click.stop="goToDetails">
        View Details
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

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

const router = useRouter();

const goToDetails = () => {
  router.push(`/journey/${props.trainNumber}`);
};
</script>

<style scoped>
.journey-card {
  background: #ffffff;
  border-radius: 18px;
  padding: 1.6rem;
  margin-bottom: 1.6rem;
  border: 1px solid #eee;
  cursor: pointer;

  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.journey-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.train-name {
  color: #555;
  font-weight: 500;
}

/* Badge */
.class-badge {
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.class-badge.ac {
  background: #e6f0ff;
  color: #0066cc;
}

.class-badge.sleeper {
  background: #fff1e6;
  color: #ff7a00;
}

.class-badge.general {
  background: #f0f0f0;
  color: #555;
}

/* Timeline */
.timeline {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  margin: 1.2rem 0;
}

.station {
  text-align: center;
}

.time {
  font-size: 1.1rem;
  font-weight: 700;
}

.code {
  font-size: 0.8rem;
  color: #666;
}

.arrow {
  font-size: 1.4rem;
  color: #0066cc;
  animation: pulse 1.8s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

/* Meta */
.meta {
  display: flex;
  gap: 1.2rem;
  font-size: 0.85rem;
  color: #666;
}

/* Footer */
.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.2rem;
}

.price {
  font-weight: 700;
  font-size: 1.1rem;
}

.stars {
  font-size: 0.85rem;
  color: #ddd;
}

.stars .filled {
  color: #ff9f1c;
}

/* Button */
.view-btn {
  background: #0066cc;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.view-btn:hover {
  background: #0052a3;
}
</style>
