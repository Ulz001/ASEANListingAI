<template>
  <div class="home">
    <h1>欢迎使用 ASEAN Listing AI</h1>
    <p class="subtitle">让跨境Listing本地化更简单、更高效</p>

    <div class="features">
      <div class="feature-card">
        <h3>🌏 多语言支持</h3>
        <p>一键翻译为泰语、越南语、印尼语、马来语、菲律宾语等东南亚主流语言</p>
      </div>

      <div class="feature-card">
        <h3>🧠 AI本地化</h3>
        <p>不只是翻译，更是本地化——根据当地文化习惯和消费偏好优化文案</p>
      </div>

      <div class="feature-card">
        <h3>⚡ 快速响应</h3>
        <p>基于大模型AI，秒级生成高质量翻译结果</p>
      </div>

      <div class="feature-card">
        <h3>📈 SEO优化</h3>
        <p>可选包含SEO建议，帮助Listing在平台内获得更好排名</p>
      </div>
    </div>

    <div class="action-section">
      <router-link to="/translate" class="btn-primary">
        开始翻译 →
      </router-link>
    </div>
  </div>
</template>

<script setup>
// 主页组件
</script>

<style scoped>
.home {
  text-align: center;
  padding: 40px 20px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 18px;
  margin-bottom: 40px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 40px 0;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.feature-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.feature-card h3 {
  margin-top: 0;
  color: #2c3e50;
}

.btn-primary {
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 15px 40px;
  border-radius: 30px;
  text-decoration: none;
  font-size: 18px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #2980b9;
}
</style>