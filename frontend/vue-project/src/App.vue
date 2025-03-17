<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<style>
:root {
  --primary-gradient: linear-gradient(120deg, #614385, #516395);
  --background-color: #f5f7fa;
  --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  --header-height: 60px;
}

body {
  margin: 0;
  padding: 0;
  background: var(--background-color);
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 统一卡片样式 */
.t-card {
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  border: none;
}

/* 统一按钮样式 */
.t-button {
  font-weight: 500;
}

/* 统一标题样式 */
.gradient-title {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: bold;
}
</style>
