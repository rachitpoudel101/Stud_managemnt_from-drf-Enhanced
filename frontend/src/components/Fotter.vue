<template>
    <div class="bg-gray-800 text-white text-center p-4">
        <p>{{ state.p }}</p>
        <p>{{ state.developer }}</p>
    </div>
</template>
<script setup>
 import { reactive } from 'vue';
 
    const state = reactive({
        p: '© 2023 SMS Application. All rights reserved.',
        developer: 'Developed by Rachit Poudel'
    });
</script>
