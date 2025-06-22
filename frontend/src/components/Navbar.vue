<template>
    <nav class="bg-gray-800 p-4">
        <div class="container mx-auto flex justify-between items-center">
        <div class="text-white text-lg font-bold">SMS Application</div>
        <div class="space-x-4">
            <router-link to="/" class="text-white hover:text-gray-300">{{ state.btn1 }}</router-link>
        </div>
        </div>
    </nav>
</template>
<script setup>
 import { reactive } from 'vue';

    const state = reactive({
        btn1: 'login' 
    });
</script>