<template>
  <div class="container">
    <h1>Fire & Intrusion Warning Dashboard</h1>
    <div class="cards">
      <SensorCard
        title="Phát hiện lửa"
        :value="fireDetected ? 'Có lửa' : 'Bình thường'"
        :warning="fireDetected"
        :warning-message="
          fireDetected ? 'Cảnh báo: Có cháy!' : 'Không có nguy cơ'
        "
      />

      <SensorCard
        title="Xâm nhập mạng"
        :value="intrusionType"
        :warning="intrusionType !== 'Bình thường'"
        :warning-message="
          intrusionType !== 'Bình thường'
            ? 'Cảnh báo: ' + intrusionType
            : 'Mạng an toàn'
        "
      />

      <SensorCard
        title="Nhiệt độ"
        :value="temperature + ' °C'"
        :warning="temperature > 50"
        :warning-message="
          temperature > 50 ? 'Cảnh báo: Nhiệt độ cao!' : 'Nhiệt độ bình thường'
        "
      />

      <SensorCard
        title="Độ ẩm"
        :value="humidity + ' %'"
        :warning="humidity > 80"
        :warning-message="
          humidity > 80 ? 'Cảnh báo: Độ ẩm cao!' : 'Độ ẩm bình thường'
        "
      />
    </div>
  </div>
</template>

<script>
import SensorCard from "../components/SensorCard.vue";

export default {
  components: { SensorCard },
  data() {
    return {
      fireDetected: false,
      intrusionType: "Bình thường",
      temperature: 30.0,
      humidity: 50.0,
    };
  },
  mounted() {
    this.fetchStatus();
    setInterval(this.fetchStatus, 3000); // gọi lại mỗi 3s
  },
  methods: {
    async fetchStatus() {
      try {
        const response = await fetch("http://localhost:5000/api/status");
        const data = await response.json();
        this.fireDetected = data.fire;
        this.intrusionType = data.intrusion;
        this.temperature = data.temperature;
        this.humidity = data.humidity;
      } catch (error) {
        console.error("Không lấy được trạng thái từ server:", error);
      }
    },
  },
};
</script>


<style>
.container {
  padding: 20px;
  font-family: Arial, sans-serif;
  text-align: center;
}
.cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 30px;
}
</style>

