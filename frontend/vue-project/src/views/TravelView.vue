<template>
  <div class="travel-container">
    <!-- 头部介绍 -->
    <div class="travel-header">
      <div class="header-content">
        <h1 class="main-title">诗意游历</h1>
        <div class="subtitle-container">
          <span>漫步诗意山水</span>
          <span class="divider">·</span>
          <span>对话先贤智慧</span>
          <span class="divider">·</span>
          <span>AI续写文化体验新篇章</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <t-card class="main-section">
      <template v-if="!selectedLocation">
        <!-- 诗人介绍 -->
        <div class="poet-intro">
          <t-comment
            :author="poetName"
            :avatar="poetAvatar"
            class="poet-comment"
          >
            <template #content>
              <div class="poet-dialogue">{{ poetDialogue }}</div>
            </template>
          </t-comment>
        </div>

        <!-- 推荐地点卡片网格 -->
        <div class="locations-section">
          <h2 class="section-title">推荐游览地点</h2>
          <div v-if="recommendedLocations.length > 0" class="locations-grid">
            <t-card
              v-for="location in recommendedLocations"
              :key="location.name"
              :title="location.name"
              class="location-card"
              theme="poster2"
              hoverable
              @click="selectLocation(location)"
            >
              <template #description>
                <p class="location-desc">{{ location.description }}</p>
              </template>
            </t-card>
          </div>
          <div v-else class="loading-container">
            <t-loading />
            <p>正在获取推荐地点...</p>
          </div>
        </div>
      </template>

      <!-- 选中地点后的展示区域 -->
      <template v-else>
        <div class="selected-location">
          <!-- 返回按钮和标题 -->
          <div class="location-header">
            <t-button theme="default" variant="text" @click="backToLocations" class="back-button">
              <template #icon><t-icon name="arrow-left" /></template>
              返回
            </t-button>
            <h2>{{ selectedLocation.name }}</h2>
          </div>

          <!-- 内容展示区域 -->
          <t-tabs class="location-tabs" :default-value="activeTab">
            <!-- 景点介绍 -->
            <t-tab-panel value="intro" label="景点介绍">
              <div class="intro-content">
                <div class="image-poetry-section">
                  <!-- 生成的图片 -->
                  <div class="image-wrapper">
                    <t-skeleton v-if="loading" animation="gradient" />
                    <img
                      v-else-if="generatedImage"
                      :src="generatedImage"
                      alt="AI生成的风景画"
                      class="generated-image"
                    />
                  </div>
                  <!-- AI生成的诗词 -->
                  <div class="poetry-section">
                    <h3>{{ poetName }}的诗词创作</h3>
                    <p class="poetry-text">{{ generatedPoetry }}</p>
                  </div>
                </div>
              </div>
            </t-tab-panel>

            <!-- 相关诗词 -->
            <t-tab-panel value="poems" label="相关诗词">
              <div class="poems-section">
                <t-empty v-if="!relatedPoems.length" description="暂无相关诗词" />
                <t-collapse v-else theme="card">
                  <t-collapse-panel
                    v-for="poem in relatedPoems"
                    :key="poem.title"
                    :header="poem.title"
                  >
                    <div class="poem-content">
                      <p class="poem-text">{{ poem.content }}</p>
                    </div>
                  </t-collapse-panel>
                </t-collapse>
              </div>
            </t-tab-panel>

            <!-- 历史典故 -->
            <t-tab-panel value="history" label="历史典故">
              <div class="history-section">
                <t-empty v-if="!locationHistory" description="暂无历史典故" />
                <div v-else class="history-content">
                  <p class="history-text">{{ locationHistory }}</p>
                </div>
              </div>
            </t-tab-panel>

            <!-- 诗人对话 -->
            <t-tab-panel value="chat" label="与诗人对话">
              <div class="chat-section">
                <div class="messages" ref="messageContainer">
                  <t-comment
                    v-for="(message, index) in messages"
                    :key="index"
                    :author="message.role === 'user' ? '你' : poetName"
                    :avatar="message.role === 'user' ? '/user.jpg' : poetAvatar"
                    :content="message.content"
                    :class="[
                      'message-item',
                      message.role === 'user' ? 'user-message' : 'bot-message'
                    ]"
                  />
                </div>
                <div class="chat-input">
                  <t-input
                    v-model="inputMessage"
                    placeholder="与诗人畅谈此处风景..."
                    :disabled="loading"
                    @keyup.enter="sendMessage"
                  >
                    <template #suffix>
                      <t-button
                        theme="primary"
                        :loading="loading"
                        @click="sendMessage"
                      >发送</t-button>
                    </template>
                  </t-input>
                </div>
              </div>
            </t-tab-panel>
          </t-tabs>
        </div>
      </template>
    </t-card>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import axios from '../utils/axios'

const route = useRoute()
const poet = route.params.poet // 从路由参数获取诗人ID

// 诗人信息
const poetInfo = computed(() => {
  const poets = {
    liqingzhao: {
      name: '李清照',
      avatar: '/liqingzhao.png'
    },
    libai: {
      name: '李白',
      avatar: '/libai.png'
    },
    dufu: {
      name: '杜甫',
      avatar: '/dufu.png'
    },
    sushi: {
      name: '苏轼',
      avatar: '/sushi.png'
    }
  }
  return poets[poet] || poets.liqingzhao
})

const poetName = computed(() => poetInfo.value.name)
const poetAvatar = computed(() => poetInfo.value.avatar)

// 状态管理
const loading = ref(false)
const poetDialogue = ref('')
const recommendedLocations = ref([])
const selectedLocation = ref(null)
const generatedPoetry = ref('')
const generatedImage = ref('')

// 添加对话相关的状态
const messages = ref([])
const inputMessage = ref('')
const messageContainer = ref(null)

// 在 script setup 中添加
const relatedPoems = ref([])
const locationHistory = ref('')

// 滚动到最新消息
const scrollToBottom = async () => {
  await nextTick()
  const container = messageContainer.value
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    MessagePlugin.warning('请输入消息')
    return
  }

  const userMessage = inputMessage.value
  messages.value.push({
    role: 'user',
    content: userMessage,
    time: new Date().toLocaleTimeString()
  })

  inputMessage.value = ''
  loading.value = true

  try {
    const response = await axios.post('/api/chat', {
      message: selectedLocation.value 
        ? `关于${selectedLocation.value.name}，${userMessage}`
        : userMessage
    })

    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      time: new Date().toLocaleTimeString()
    })
  } catch (error) {
    MessagePlugin.error('发送消息失败')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 初始化获取诗人对话和推荐地点
const initializeTravel = async (poet) => {
  loading.value = true
  try {
    const response = await axios.post('/api/travel/init', { poet: poet })
    poetDialogue.value = response.data.dialogue
    recommendedLocations.value = response.data.locations || []

    if (!response.data.locations || response.data.locations.length === 0) {
      MessagePlugin.warning('未获取到推荐地点')
    }
  } catch (error) {
    MessagePlugin.error('初始化失败')
  } finally {
    loading.value = false
  }
}

// 选择地点
const selectLocation = async (location) => {
  selectedLocation.value = location
  loading.value = true
  messages.value = [] // 清空之前的对话

  try {
    console.log('开始获取地点数据:', location.name)

    const [poetryResponse, imageResponse, locationResponse] = await Promise.all([
      axios.post('/api/generate-poetry', { 
        location: location.name,
        poet: poet
      }),
      axios.post('/api/generate-image', { location: location.name }),
      axios.get(`/api/location/poems/${encodeURIComponent(location.name)}`)
    ])

    console.log('地点信息响应:', locationResponse.data)

    if (poetryResponse.data.poetry) {
      generatedPoetry.value = poetryResponse.data.poetry
    }
    
    if (imageResponse.data.imageUrl) {
      generatedImage.value = imageResponse.data.imageUrl
    }

    // 更新相关诗词和历史典故
    if (locationResponse.data.poems) {
      relatedPoems.value = locationResponse.data.poems
    }
    
    if (locationResponse.data.history) {
      locationHistory.value = locationResponse.data.history
    }

    // 添加诗人的初始对话
    messages.value.push({
      role: 'assistant',
      content: `让我为你介绍${location.name}的美景...`,
      time: new Date().toLocaleTimeString()
    })
  } catch (error) {
    console.error('获取数据失败:', error.response || error)
    MessagePlugin.error(error.response?.data?.error || '获取数据失败')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 返回地点选择时清空数据
const backToLocations = () => {
  selectedLocation.value = null
  generatedPoetry.value = ''
  generatedImage.value = ''
  relatedPoems.value = []
  locationHistory.value = ''
}

// 添加分类和标签数据
const categories = [
  { label: '全部', value: 'all' },
  { label: '山水', value: 'nature' },
  { label: '人文', value: 'culture' },
  { label: '建筑', value: 'architecture' }
]

const tags = ['名胜古迹', '自然风光', '文化遗产', '诗词典故', '历史遗迹']
const currentCategory = ref('all')
const selectedTags = ref([])

// 过滤地点
const filteredLocations = computed(() => {
  let locations = recommendedLocations.value
  
  if (currentCategory.value !== 'all') {
    locations = locations.filter(loc => loc.category === currentCategory.value)
  }
  
  if (selectedTags.value.length > 0) {
    locations = locations.filter(loc => 
      loc.tags?.some(tag => selectedTags.value.includes(tag))
    )
  }
  
  return locations
})

// 初始化
initializeTravel(poet)

const activeTab = ref('intro')
</script>

<style scoped>
.travel-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.travel-header {
  margin-bottom: 24px;
}

.header-content {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
}

.main-title {
  font-size: 2.6rem;
  font-weight: bold;
  margin: 0 0 12px;
  background: linear-gradient(120deg, #614385, #516395);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 3px;
}

.subtitle-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  color: var(--td-text-color-secondary);
  font-size: 1rem;
}

.divider {
  color: var(--td-brand-color);
  opacity: 0.5;
}

@media (max-width: 768px) {
  .travel-header {
    margin-bottom: 20px;
  }

  .header-content {
    padding: 15px;
  }

  .main-title {
    font-size: 2.2rem;
    margin-bottom: 8px;
  }

  .subtitle-container {
    flex-direction: column;
    gap: 8px;
  }

  .divider {
    display: none;
  }
}

/* 添加动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.main-title {
  animation: fadeInUp 1s ease-out;
}

.subtitle-item {
  animation: fadeInUp 1s ease-out forwards;
}

.subtitle-item:nth-child(1) {
  animation-delay: 0.2s;
}

.subtitle-item:nth-child(3) {
  animation-delay: 0.4s;
}

.subtitle-item:nth-child(5) {
  animation-delay: 0.6s;
}

.main-section {
  padding: 24px;
}

.poet-intro {
  margin-bottom: 40px;
  padding: 24px;
  background: linear-gradient(to right, #f8f9fa, #ffffff);
  border-radius: 12px;
}

.poet-dialogue {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--td-text-color-primary);
}

.section-title {
  font-size: 1.8rem;
  margin-bottom: 24px;
  text-align: center;
  color: var(--td-text-color-primary);
}

.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.location-card {
  height: 100%;
  transition: transform 0.2s ease;
}

.location-card:hover {
  transform: translateY(-4px);
}

.location-desc {
  font-size: 1rem;
  line-height: 1.8;
  color: var(--td-text-color-secondary);
  padding: 16px;
  text-align: justify;
  margin: 0;
}

.selected-location {
  padding: 0;
}

.location-header {
  display: flex;
  align-items: center;
  margin-bottom: 32px;
}

.location-header h2 {
  font-size: 2rem;
  margin: 0;
  flex-grow: 1;
  text-align: center;
}

.back-button {
  font-size: 1.1rem;
}

.image-poetry-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

.image-wrapper {
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.generated-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poetry-section {
  padding: 24px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
}

.poetry-text {
  font-size: 1.2rem;
  line-height: 2;
  white-space: pre-wrap;
  text-align: center;
}

.poem-content, .history-content {
  padding: 24px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.poem-text {
  font-size: 1.1rem;
  line-height: 2;
  text-align: center;
  margin: 0;
  white-space: pre-wrap;
}

.history-text {
  font-size: 1.1rem;
  line-height: 1.8;
  margin: 0;
  text-align: justify;
  text-indent: 2em;
}

.chat-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 500px;
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
}

.message-item {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: var(--td-radius-medium);
}

.user-message {
  background-color: rgba(0, 82, 217, 0.05);
}

.bot-message {
  background-color: rgba(0, 0, 0, 0.02);
}

@media (max-width: 768px) {
  .image-poetry-section {
    grid-template-columns: 1fr;
  }

  .travel-header h1 {
    font-size: 2.5rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .locations-grid {
    grid-template-columns: 1fr;
  }
}
</style> 