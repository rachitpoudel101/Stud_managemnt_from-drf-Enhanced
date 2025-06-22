<script setup>
import Navbar from './components/Navbar.vue'
import Fotter from './components/Fotter.vue'
import Home from './views/Home.vue'
</script>

<template>
<div class="min-h-screen flex flex-col bg-gray-100 font-sans">
  <Navbar />
  <Home />
  <div class="mt-auto bg-gray-100">  
    <Fotter />
  </div>
</div>
</template>
