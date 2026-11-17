<template>
  <main class="shell">
    <h1>咨询预约平台</h1>
    <p class="lead">工程骨架已就绪。业务实现待按 iteration1 规格落地。</p>
    <ul>
      <li>需求规格：<code>docs/features/iteration1/</code></li>
      <li>交互原型：<code>docs/features/iteration1/prototypes/</code>（端口 5174）</li>
      <li>健康检查：<code>GET /api/v1/health</code></li>
    </ul>
  </main>
</template>

<style scoped>
.shell {
  max-width: 40rem;
  margin: 4rem auto;
  padding: 0 1.5rem;
  font-family: system-ui, sans-serif;
  line-height: 1.6;
}
h1 { font-size: 1.75rem; margin-bottom: 0.5rem; }
.lead { color: #555; margin-bottom: 1.5rem; }
ul { padding-left: 1.25rem; }
code { font-size: 0.9em; background: #f3f4f6; padding: 0.1em 0.35em; border-radius: 4px; }
</style>
