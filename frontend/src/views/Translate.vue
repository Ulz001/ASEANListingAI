<template>
  <div class="container">
    <h1>🌏 ASEAN Listing AI - 跨境本地化工具</h1>
    <p>将英文Listing快速翻译并本地化为东南亚语言</p>

    <div class="input-section">
      <textarea
        v-model="formData.sourceText"
        placeholder="请输入英文产品描述/Listing内容..."
        rows="6"
      ></textarea>

      <div class="form-row">
        <select v-model="formData.targetLanguage">
          <option value="th">泰语 (TH)</option>
          <option value="vi">越南语 (VI)</option>
          <option value="id">印尼语 (ID)</option>
          <option value="ms">马来语 (MS)</option>
          <option value="fil">菲律宾语 (FIL)</option>
          <option value="th">英语 (保持原文)</option>
        </select>

        <select v-model="formData.tone">
          <option value="professional">专业正式</option>
          <option value="casual">轻松友好</option>
          <option value="formal">正式严谨</option>
        </select>

        <button @click="translate" :disabled="loading">
          {{ loading ? '处理中...' : '开始翻译' }}
        </button>
      </div>

      <label>
        <input type="checkbox" v-model="formData.includeSEO">
        包含SEO优化建议
      </label>
    </div>

    <div v-if="result" class="result-section">
      <h3>翻译结果：</h3>
      <div class="result-box">{{ result.translatedText }}</div>

      <div v-if="result.seoSuggestions && result.seoSuggestions.length > 0" class="seo-box">
        <h4>💡 SEO优化建议：</h4>
        <ul>
          <li v-for="(suggestion, i) in result.seoSuggestions" :key="i">
            {{ suggestion }}
          </li>
        </ul>
      </div>

      <div class="meta">
        <small>请求ID: {{ result.requestId }} | {{ result.createdAt }}</small>
      </div>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 表单数据
const formData = ref({
  sourceText: '',
  targetLanguage: 'th',
  tone: 'professional',
  includeSEO: false
})

// 结果和错误状态
const result = ref(null)
const error = ref(null)
const loading = ref(false)

// 翻译函数
async function translate() {
  if (!formData.value.sourceText.value) {
    error.value = '请输入产品描述内容'
    return
  }

  loading.value = true
  error.value = null
  result.value = null

  try {
    const response = await axios.post(
      'http://localhost:8000/translate',
      {
        sourceText: formData.value.sourceText,
        targetLanguage: formData.value.targetLanguage,
        tone: formData.value.tone,
        includeSEO: formData.value.includeSEO
      },
      { headers: { 'Content-Type': 'application/json' } }
    )

    result.value = {
      translatedText: response.data.translatedText,
      seoSuggestions: response.data.seoSuggestions || [],
      requestId: response.data.requestId,
      createdAt: new Date(response.data.createdAt).toLocaleString()
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '翻译失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  text-align: left;
}

.input-section textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
}

.form-row {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.form-row select, .form-row button {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-row button {
  background-color: #3498db;
  color: white;
  cursor: pointer;
  min-width: 120px;
}

.form-row button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.result-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.result-box {
  background-color: white;
  padding: 20px;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  margin-top: 15px;
  white-space: pre-wrap;
  line-height: 1.6;
}

.seo-box {
  margin-top: 20px;
  padding: 15px;
  background-color: #e8f4fd;
  border-radius: 6px;
  border-left: 4px solid #3498db;
}

.error {
  color: #e74c3c;
  background-color: #fadbd8;
  padding: 15px;
  border-radius: 6px;
  margin-top: 20px;
}
</style>