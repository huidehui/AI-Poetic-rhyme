<template>
  <div class="home-container">
    <!-- 头部横幅 -->
    <div class="hero-section">
      <h1 class="hero-title">诗词复兴</h1>
      <p class="hero-subtitle">与古代诗人对话，感受千年文化</p>
    </div>

    <!-- 诗人卡片区域 -->
    <div class="poets-section">
      <div class="poets-grid">
        <t-card
          v-for="poet in poets"
          :key="poet.id"
          :title="poet.name"
          class="poet-card"
          theme="poster2"
          :hover-shadow="true"
        >
          <template #cover>
            <div class="avatar-wrapper">
              <img :src="poet.avatar" :alt="poet.name" class="poet-avatar"/>
            </div>
          </template>
          <template #description>
            <p class="poet-description">{{ poet.description }}</p>
          </template>
          <template #footer>
            <t-space align="center" class="poet-actions">
              <t-button theme="primary" shape="round" @click="startChat(poet)">开始对话</t-button>
              <t-button theme="default" shape="round" @click="startTravel(poet)">诗意游历</t-button>
            </t-space>
          </template>
        </t-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const poets = ref([
  {
    id: 'liqingzhao',
    name: '李清照',
    avatar: '/liqingzhao.png',
    description: '宋代女词人，"千古第一才女"，婉约词派代表人物。'
  },
  {
    id: 'libai',
    name: '李白',
    avatar: '/libai.png',
    description: '唐代伟大的浪漫主义诗人，被称为"诗仙"。'
  }
])

const startChat = (poet) => {
  router.push(`/chat/${poet.id}`)
}

const startTravel = (poet) => {
  router.push(`/travel/${poet.id}`)
}
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.hero-section {
  text-align: center;
  padding: 30px 20px;
  background: var(--primary-gradient);
  color: white;
  margin-bottom: 30px;
  border-radius: 12px;
}

.hero-title {
  font-size: 2.6rem;
  font-weight: bold;
  margin-bottom: 8px;
  letter-spacing: 3px;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.15);
}

.hero-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.4;
}

.poets-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 0;
}

.poets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 40px;
  justify-items: center;
}

.poet-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.avatar-wrapper {
  height: 200px;
  position: relative;
  overflow: hidden;
  border-radius: 12px 12px 0 0;
}

.poet-avatar {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 80%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.poet-card:hover .poet-avatar {
  transform: translate(-50%, -50%) scale(1.05);
}

.poet-description {
  color: var(--td-text-color-secondary);
  line-height: 1.6;
  margin: 16px 0;
  text-align: center;
}

.poet-actions {
  padding: 16px 0;
  gap: 12px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .hero-section {
    padding: 25px 20px;
  }

  .hero-title {
    font-size: 2.2rem;
    letter-spacing: 2px;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .poets-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
  }
}
</style>
