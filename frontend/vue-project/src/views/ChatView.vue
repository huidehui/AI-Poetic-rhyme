<template>
  <div class="chat-container">
    <t-card :title="`与${poetName}对话`">
      <div class="chat-messages" ref="messageContainer">
        <template v-for="(message, index) in messages" :key="index">
          <t-comment
            :author="message.role === 'user' ? '你' : poetName"
            :avatar="message.role === 'user' ? '/user.jpg' : poetAvatar"
            :datetime="message.time"
            :content="message.content"
            :class="[
              'message-item',
              message.role === 'user' ? 'user-message' : 'bot-message'
            ]"
          >
            <template #avatar-slot>
              <t-avatar
                :image="message.role === 'user' ? '/user.jpg' : poetAvatar"
                :size="48"
              />
            </template>
          </t-comment>
        </template>
      </div>

      <div class="chat-input">
        <t-space direction="vertical" size="large">
          <t-form-item>
            <input
              v-model="inputMessage"
              type="text"
              class="t-input"
              placeholder="在此输入你想说的话..."
              @keyup.enter="sendMessage"
            />
          </t-form-item>

          <t-button 
            block 
            @click="sendMessage"
            :loading="loading"
          >
            发送
          </t-button>
        </t-space>
      </div>
    </t-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import axios from '../utils/axios'

const route = useRoute()
const poet = route.params.poet

const poetInfo = computed(() => {
  const poets = {
    liqingzhao: {
      name: '李清照',
      avatar: '/liqingzhao.png'
    },
    libai: {
      name: '李白',
      avatar: '/libai.png'
    }
  }
  return poets[poet] || poets.liqingzhao
})

const poetName = computed(() => poetInfo.value.name)
const poetAvatar = computed(() => poetInfo.value.avatar)

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messageContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  const container = messageContainer.value
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    MessagePlugin.warning('请输入消息')
    return
  }

  const userMessage = inputMessage.value
  const message = {
    role: 'user',
    content: userMessage,
    time: new Date().toLocaleTimeString()
  }

  messages.value.push(message)
  inputMessage.value = ''
  loading.value = true

  try {
    const response = await axios.post('/api/chat', {
      message: userMessage
    })

    if (!response.data || !response.data.response) {
      throw new Error('服务器响应格式错误')
    }

    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      time: new Date().toLocaleTimeString()
    })
  } catch (error) {
    console.error('发送消息失败:', error)
    MessagePlugin.error(`发送消息失败: ${error.message || '未知错误'}`)
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chat-main {
  background: white;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 24px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
  margin-bottom: 24px;
}

.message-input {
  padding: 16px;
  border-top: 1px solid var(--td-component-border);
}

.t-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--td-component-border);
  border-radius: var(--td-radius-default);
  font-size: 14px;
  line-height: 22px;
  transition: all 0.2s;
}

.t-input:focus {
  border-color: var(--td-brand-color);
  outline: none;
}

.message-item {
  margin-bottom: 20px;
  padding: 12px;
  border-radius: var(--td-radius-medium);
}

.message-item :deep(.t-comment__inner) {
  display: flex;
  gap: 16px;
}

.message-item :deep(.t-comment__avatar) {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
}

.message-item :deep(.t-comment__avatar img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-item :deep(.t-comment__content) {
  flex: 1;
}

.user-message {
  background-color: rgba(0, 82, 217, 0.05);
}

.bot-message {
  background-color: rgba(0, 0, 0, 0.02);
}

.t-avatar {
  width: 48px !important;
  height: 48px !important;
}

.t-avatar :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.t-comment__content :deep(pre) {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
}
</style>
