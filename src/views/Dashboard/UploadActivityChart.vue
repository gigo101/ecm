<script setup>
import { ref, onMounted } from "vue"
import { Chart, registerables } from "chart.js"
import api from "@/api"

Chart.register(...registerables)

const canvasRef = ref(null)

async function loadChart() {
  const res = await api.get("/dashboard/upload-activity")

  const labels = res.data.map(i => i.label)
  const data = res.data.map(i => i.count)

  new Chart(canvasRef.value, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Uploads",
          data,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      }
    }
  })
}

onMounted(loadChart)
</script>

<template>
  <div class="bg-white p-6 rounded shadow">
    <div class="text-sm text-gray-500 mb-3">
      Upload Activity
    </div>
    <canvas ref="canvasRef"></canvas>
  </div>
</template>