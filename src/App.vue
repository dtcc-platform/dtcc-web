<template>
  <div>
    <HeaderNav />
    <HeroSection />
    <IntroSection />
    <GradientFeature />
    <WhatAreTwins />
    <NewsSection />
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
import GradientFeature from './components/GradientFeature.vue'
import WhatAreTwins from './components/WhatAreTwins.vue'
import NewsSection from './components/NewsSection.vue'
import ProjectsSection from './components/ProjectsSection.vue'
import SocialFeed from './components/SocialFeed.vue'  // Loaded eagerly to fix navigation
import FooterSection from './components/FooterSection.vue'
import LoadingSpinner from './components/LoadingSpinner.vue'

// Lazy load below-the-fold components - loads when user scrolls
// Note: SocialFeed is now eagerly loaded since it's a navigation target (#linkedin-feed)

const CTAStudents = defineAsyncComponent({
  loader: () => import('./components/CTAStudents.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
  timeout: 10000
})
</script>

<style>
/* Page-level tweaks can go here if needed */
</style>

