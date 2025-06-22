<template>
  <section class="max-w-4xl mx-auto my-12 p-8 bg-gray-50 rounded-lg shadow">
    <h1 class="text-3xl font-bold mb-4 text-gray-800">{{ state.h1 }}</h1>
    <p class="mb-4 text-gray-700 text-lg">
      {{ state.p1 }}
    </p>
    <p class="mb-4 text-gray-700">{{ state.p2 }}</p>
    <div class="my-8">
      <h2 class="text-2xl font-semibold text-gray-800 mb-4">{{ state.p3 }}</h2>
      <ul class="space-y-2 text-gray-700 list-disc list-inside">
        <li>{{ state.features[0] }}</li>
        <li>{{ state.features[1] }}</li>
        <li>{{ state.features[2] }}</li>
        <li>{{ state.features[3] }}</li>
        <li>{{ state.features[4] }}</li>
      </ul>
    </div>
  </section>
</template>
<script setup>
import { reactive } from 'vue';
const state = reactive({
    h1: '📘 Welcome to the Student Management System',
    p1: 'This platform simplifies how students, teachers, and admins manage academic data.',
    p2: '🎯 Explore the dashboard to manage student records, monitor performance and streamline communication.',
    p3: '✨ Key Features!',
    features: [
        '👨‍🏫 Role-based Access Control (Admin, Teacher, Student)',
        '🗃️ Student Profile Management',
        '📊 Marks & GPA Tracking',
        '📅 Attendance Recording',
        '🗂️ Subject & Class Management'
    ]
});
</script>
