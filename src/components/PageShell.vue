<template>
  <div>
    <HeaderNav />
    <slot />
    <CTAStudents v-if="showCTA" />
    <FooterSection />
  </div>
</template>

<script setup>
import HeaderNav from './HeaderNav.vue'
import CTAStudents from './CTAStudents.vue'
import FooterSection from './FooterSection.vue'

defineProps({
  /**
   * Whether to show the CTA (Call to Action) section for students.
   * Defaults to true for most pages.
   */
  showCTA: {
    type: Boolean,
    default: true
  }
})
</script>

<style>
/* Page shell uses global styles - no scoped styles needed */
</style>
