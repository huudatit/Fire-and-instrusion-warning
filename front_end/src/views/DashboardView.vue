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
  import axios from "axios";
  
  export default {
    components: { SensorCard },
    data() {
      return {
        fireDetected: false,
        intrusionType: "Bình thường",
        temperature: 60.0,
        humidity: 50.0,
      };
    },
    mounted() {
      this.fetchSensorData();
      setInterval(this.fetchSensorData, 3000);
    },
    methods: {
      fetchSensorData() {
        axios
          .get("https://fire-and-instrusion-warning.onrender.com/api/status")
          .then((res) => {
            this.fireDetected = res.data.fire;
            this.intrusionType = res.data.intrusion;
            this.temperature = res.data.temperature;
            this.humidity = res.data.humidity;
          });
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
  