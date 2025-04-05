<script>
export default {
  props: {
    title: {
      type: String,
      default: "Không có tiêu đề"
    },
    value: {
      type: String,
      default: "-"
    },
    warning: {
      type: Boolean,
      default: false
    },
    warningMessage: {
      type: String,
      default: "Không có cảnh báo"
    }
  }
};
</script>

<template>
  <div class="card">
    <div class="card-header">
      {{ title }}
    </div>
    <div class="card-value">
      {{ value }}
    </div>
    <div 
      class="card-warning" 
      :class="{ alert: warning }"
    >
      {{ warningMessage }}
    </div>
  </div>
</template>

<style scoped>
.card {
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 15px;
  text-align: center;
  width: 220px;
  margin: 10px;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
}
.card-header {
  font-weight: bold;
  background: #007bff;
  color: white;
  padding: 8px;
  border-radius: 8px 8px 0 0;
}
.card-value {
  font-size: 24px;
  margin: 10px 0;
}
.card-warning {
  font-size: 14px;
  color: #333;
}
.card-warning.alert {
  color: red;
  font-weight: bold;
}
</style>
