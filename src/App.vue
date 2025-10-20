<template>
  <div>
    <HeaderNav />
    <HeroSection />
    <IntroSection />
    <NewsSection />
    <GradientFeature />
    <WhatAreTwins />
    <ProjectsSection />
    <SocialFeed />
    <CTAStudents />
    <FooterSection />
  </div>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'
import HeaderNav from './components/HeaderNav.vue'
import HeroSection from './components/HeroSection.vue'
import IntroSection from './components/IntroSection.vue'
import NewsSection from './components/NewsSection.vue'
import GradientFeature from './components/GradientFeature.vue'
import WhatAreTwins from './components/WhatAreTwins.vue'
import ProjectsSection from './components/ProjectsSection.vue'
import FooterSection from './components/FooterSection.vue'

// Lazy load below-the-fold components - loads when user scrolls
const SocialFeed = defineAsyncComponent(() => import('./components/SocialFeed.vue'))
const CTAStudents = defineAsyncComponent(() => import('./components/CTAStudents.vue'))
</script>

<style>
/* Page-level tweaks can go here if needed */
</style>

