<template>
  <div class="container">
    <h1>Fire & Intrusion Warning Dashboard</h1>
    <nav>
      <router-link to="/">Trang chính</router-link> |
      <router-link to="/admin">Giả lập tấn công</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {};
</script>
