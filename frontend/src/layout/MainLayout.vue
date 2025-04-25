  <!-- 管理员菜单 -->
  <template v-if="userInfo.is_admin">
    <el-sub-menu index="admin">
      <template #title>
        <el-icon><Setting /></el-icon>
        <span>系统管理</span>
      </template>
      <el-menu-item index="/admin/users">用户管理</el-menu-item>
      <el-menu-item index="/admin/statistics">MCP统计</el-menu-item>
    </el-sub-menu>
  </template> 