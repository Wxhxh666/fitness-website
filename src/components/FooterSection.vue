<template>
  <footer class="site-footer">
    <div class="container">
      <div class="site-footer__grid">
        <div class="site-footer__brand">
          <div class="site-footer__logo">
            <span class="site-footer__logo-mark">F</span>
            <span class="site-footer__logo-text">FITLUXE</span>
          </div>
          <p class="site-footer__tagline">以科学重塑身体 · 以优雅成就非凡</p>
        </div>
        <div class="site-footer__links">
          <h4 class="site-footer__heading">快速导航</h4>
          <router-link to="/">首页</router-link>
          <router-link to="/exercises">动作教学</router-link>
          <router-link to="/plans">计划制定</router-link>
          <router-link to="/body-data">身材数据管理</router-link>
          <router-link to="/contact">联系</router-link>
        </div>
        <div class="site-footer__links">
          <h4 class="site-footer__heading">联系方式</h4>
          <a href="mailto:hello@fitluxe.com">hello@fitluxe.com</a>
          <a href="tel:+862161883000">+86 21 6188 3000</a>
          <span>上海市静安区南京西路1788号</span>
        </div>
        <div class="site-footer__social">
          <h4 class="site-footer__heading">关注我们</h4>
          <div class="site-footer__social-icons">
            <a href="#" class="social-icon">WeChat</a>
            <a href="#" class="social-icon">Weibo</a>
            <a href="#" class="social-icon">RED</a>
            <a href="#" class="social-icon">DouYin</a>
          </div>
        </div>
      </div>
      <div class="site-footer__bottom">
        <p>&copy; 2026 FITLUXE. All rights reserved.</p>
        <p class="site-footer__legal">沪ICP备xxxxxxxx号</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background: var(--clr-bg-dark); color: var(--clr-gray-lighter);
  padding: 80px 0 40px;
  border-top: 1px solid rgba(201, 169, 110, 0.1);
}
.site-footer__grid {
  display: grid; grid-template-columns: 1.8fr 1fr 1fr 1fr; gap: 48px; margin-bottom: 60px;
}
.site-footer__logo { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.site-footer__logo-mark {
  font-family: var(--font-display); font-size: 28px; font-weight: 600;
  color: var(--clr-gold); font-style: italic;
}
.site-footer__logo-text {
  font-family: var(--font-display); font-size: 18px; font-weight: 400;
  letter-spacing: 3px; color: var(--clr-cream);
}
.site-footer__tagline { font-size: 14px; color: var(--clr-gray); letter-spacing: 1px; line-height: 1.6; }
.site-footer__heading {
  font-family: var(--font-display); font-size: 14px; font-weight: 400;
  letter-spacing: 2px; color: var(--clr-cream); margin-bottom: 20px;
}
.site-footer__links { display: flex; flex-direction: column; gap: 12px; }
.site-footer__links a, .site-footer__links span {
  font-size: 13px; color: var(--clr-gray); letter-spacing: 0.5px;
  text-decoration: none; transition: var(--transition-default);
}
.site-footer__links a:hover { color: var(--clr-gold-light); }
.site-footer__social-icons { display: flex; flex-wrap: wrap; gap: 12px; }
.social-icon {
  padding: 8px 14px; font-size: 11px; letter-spacing: 1px;
  color: var(--clr-gray); text-decoration: none;
  border: 1px solid var(--clr-gray-deep); transition: var(--transition-default);
}
.social-icon:hover { color: var(--clr-gold); border-color: var(--clr-gold); }
.site-footer__bottom {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 32px; border-top: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 12px; color: var(--clr-gray-deep);
}
.site-footer__legal { color: var(--clr-gray-deep); }

@media (max-width: 768px) {
  .site-footer__grid { grid-template-columns: 1fr; gap: 36px; }
  .site-footer__bottom { flex-direction: column; gap: 8px; text-align: center; }
}
</style>

