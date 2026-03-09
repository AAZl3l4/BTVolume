"""
GUI界面模块 - 主窗口界面
使用tkinter实现轻量级GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)


class MainWindow:
    """主窗口类"""
    
    def __init__(self, app):
        """
        初始化主窗口
        
        Args:
            app: 主应用实例
        """
        self.app = app
        self.root = None
        self.is_visible = False
        
        # UI组件引用
        self.volume_var = None
        self.preset_listbox = None
        self.task_tree = None
        self.bt_status_label = None
    
    def create_window(self):
        """创建主窗口"""
        if self.root is not None:
            return
        
        self.root = tk.Tk()
        self.root.title('蓝牙耳机音量控制')
        self.root.geometry('550x650')
        self.root.resizable(False, False)
        
        # 设置窗口类名（用于单实例查找）
        self.root.wm_classname = 'BluetoothVolumeControl_MainWindow'
        
        # 设置窗口图标
        self._set_window_icon()
        
        # 设置窗口关闭行为
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)
        
        # 创建UI
        self._create_ui()
        
        # 更新显示
        self._update_ui()
    
    def _create_ui(self):
        """创建用户界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding='10')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== 当前音量显示 ==========
        volume_frame = ttk.LabelFrame(main_frame, text='当前音量', padding='10')
        volume_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 音量输入框和设置按钮
        volume_input_frame = ttk.Frame(volume_frame)
        volume_input_frame.pack(fill=tk.X)
        
        # 获取当前系统音量作为默认值
        current_vol = self.app.audio_controller.get_volume()
        self.volume_var = tk.StringVar(value=str(current_vol))
        volume_entry = ttk.Entry(
            volume_input_frame,
            textvariable=self.volume_var,
            width=10,
            justify='center'
        )
        volume_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(volume_input_frame, text='%').pack(side=tk.LEFT, padx=(0, 10))
        
        set_btn = ttk.Button(
            volume_input_frame,
            text='设置音量',
            command=self._on_set_volume
        )
        set_btn.pack(side=tk.LEFT)
        
        # 显示当前系统音量
        self.volume_label = ttk.Label(volume_frame, text='当前系统音量: --', foreground='gray')
        self.volume_label.pack(pady=(5, 0))
        
        # ========== 蓝牙状态 ==========
        bt_frame = ttk.LabelFrame(main_frame, text='蓝牙状态', padding='10')
        bt_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.bt_status_label = ttk.Label(bt_frame, text='检测中...', foreground='gray')
        self.bt_status_label.pack(side=tk.LEFT)
        
        # ========== 预设音量 ==========
        preset_frame = ttk.LabelFrame(main_frame, text='预设音量 (托盘菜单)', padding='10')
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 预设音量列表
        list_frame = ttk.Frame(preset_frame)
        list_frame.pack(fill=tk.X)
        
        self.preset_listbox = tk.Listbox(list_frame, height=4, selectmode=tk.SINGLE)
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.preset_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preset_listbox.config(yscrollcommand=scrollbar.set)
        
        # 预设音量操作按钮
        btn_frame = ttk.Frame(preset_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.new_preset_var = tk.StringVar()
        preset_entry = ttk.Entry(btn_frame, textvariable=self.new_preset_var, width=10)
        preset_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        add_btn = ttk.Button(btn_frame, text='添加', command=self._add_preset)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(btn_frame, text='删除', command=self._remove_preset)
        remove_btn.pack(side=tk.LEFT)
        
        # ========== 定时任务 ==========
        task_frame = ttk.LabelFrame(main_frame, text='定时任务', padding='10')
        task_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 任务列表
        tree_frame = ttk.Frame(task_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('time', 'volume', 'enabled')
        self.task_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=4
        )
        
        self.task_tree.heading('time', text='时间')
        self.task_tree.heading('volume', text='音量')
        self.task_tree.heading('enabled', text='启用')
        
        self.task_tree.column('time', width=100, anchor='center')
        self.task_tree.column('volume', width=100, anchor='center')
        self.task_tree.column('enabled', width=60, anchor='center')
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.config(yscrollcommand=tree_scrollbar.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.task_tree.bind('<Double-1>', self._on_task_double_click)
        
        # 任务操作按钮
        task_btn_frame = ttk.Frame(task_frame)
        task_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 时间输入
        ttk.Label(task_btn_frame, text='时间:').pack(side=tk.LEFT)
        self.task_hour_var = tk.StringVar(value='08')
        hour_spin = ttk.Spinbox(task_btn_frame, from_=0, to=23, width=3, textvariable=self.task_hour_var, format='%02.0f')
        hour_spin.pack(side=tk.LEFT, padx=(2, 0))
        
        ttk.Label(task_btn_frame, text=':').pack(side=tk.LEFT)
        
        self.task_minute_var = tk.StringVar(value='00')
        minute_spin = ttk.Spinbox(task_btn_frame, from_=0, to=59, width=3, textvariable=self.task_minute_var, format='%02.0f')
        minute_spin.pack(side=tk.LEFT, padx=(2, 5))
        
        # 音量输入
        ttk.Label(task_btn_frame, text='音量:').pack(side=tk.LEFT)
        self.task_volume_var = tk.StringVar(value='50')
        volume_entry = ttk.Entry(task_btn_frame, textvariable=self.task_volume_var, width=5)
        volume_entry.pack(side=tk.LEFT, padx=(2, 5))
        
        # 添加/保存按钮（动态切换）
        self.add_task_btn = ttk.Button(task_btn_frame, text='添加', command=self._add_task)
        self.add_task_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_task_btn = ttk.Button(task_btn_frame, text='删除', command=self._remove_task)
        remove_task_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        toggle_task_btn = ttk.Button(task_btn_frame, text='启用/禁用', command=self._toggle_task)
        toggle_task_btn.pack(side=tk.LEFT)
        
        # 当前编辑的任务ID（-1表示没有正在编辑的任务）
        self.editing_task_id = -1
        
        # ========== 底部按钮 ==========
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        # 开机自启动复选框
        self.auto_start_var = tk.BooleanVar(value=self.app.config.is_auto_start_enabled())
        auto_start_cb = ttk.Checkbutton(
            bottom_frame,
            text='开机自启动',
            variable=self.auto_start_var,
            command=self._on_auto_start_changed
        )
        auto_start_cb.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = ttk.Button(bottom_frame, text='保存设置', command=self._save_config)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        minimize_btn = ttk.Button(bottom_frame, text='最小化到托盘', command=self.hide)
        minimize_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        exit_btn = ttk.Button(bottom_frame, text='退出', command=self._on_exit)
        exit_btn.pack(side=tk.RIGHT)
    
    def _set_window_icon(self):
        """设置窗口图标"""
        try:
            from tray_icon import create_app_icon
            import tempfile
            import os
            
            # 创建图标
            icon_image = create_app_icon()
            
            # 保存为临时ICO文件
            temp_dir = tempfile.gettempdir()
            icon_path = os.path.join(temp_dir, 'bt_volume_icon.ico')
            
            # 转换为RGB模式并保存
            icon_rgb = icon_image.convert('RGBA')
            icon_rgb.save(icon_path, format='ICO', sizes=[(64, 64)])
            
            # 设置窗口图标
            self.root.iconbitmap(icon_path)
            
        except Exception as e:
            logger.error(f"设置窗口图标失败: {e}")
    
    def _update_ui(self):
        """更新UI显示"""
        # 更新当前系统音量显示
        current_volume = self.app.audio_controller.get_volume()
        self.volume_label.config(text=f'当前系统音量: {current_volume}%')
        
        # 更新预设音量列表
        self._update_preset_list()
        
        # 更新任务列表
        self._update_task_list()
        
        # 更新蓝牙状态
        self._refresh_bluetooth_status()
    
    def _update_preset_list(self):
        """更新预设音量列表"""
        self.preset_listbox.delete(0, tk.END)
        presets = self.app.config.get_preset_volumes()
        for volume in presets:
            self.preset_listbox.insert(tk.END, f'{volume}%')
    
    def _update_task_list(self):
        """更新任务列表"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        tasks = self.app.config.get_scheduled_tasks()
        for task in tasks:
            enabled_text = '是' if task.get('enabled', True) else '否'
            self.task_tree.insert(
                '',
                tk.END,
                values=(task['time'], f"{task['volume']}%", enabled_text),
                tags=(str(task.get('id', 0)),)
            )
    
    def _refresh_bluetooth_status(self):
        """刷新蓝牙状态显示"""
        try:
            if self.app.bluetooth_checker.is_bluetooth_connected():
                devices = self.app.bluetooth_checker.get_connected_bluetooth_devices()
                if devices:
                    device_names = ', '.join(devices[:2])  # 最多显示2个设备
                    if len(devices) > 2:
                        device_names += f' 等{len(devices)}个设备'
                    self.bt_status_label.config(
                        text=f'已连接: {device_names}',
                        foreground='green'
                    )
                else:
                    self.bt_status_label.config(text='已连接', foreground='green')
            else:
                self.bt_status_label.config(text='未连接蓝牙耳机', foreground='red')
        except Exception as e:
            logger.error(f"刷新蓝牙状态失败: {e}")
            self.bt_status_label.config(text='检测失败', foreground='orange')
    
    def _on_set_volume(self):
        """设置音量按钮回调"""
        try:
            volume = int(self.volume_var.get())
            volume = max(0, min(100, volume))
            self.app.set_volume(volume)
            # 更新显示
            self.volume_label.config(text=f'当前系统音量: {volume}%')
        except ValueError:
            messagebox.showerror('错误', '请输入有效的音量值(0-100)')
    
    def _add_preset(self):
        """添加预设音量"""
        try:
            volume = int(self.new_preset_var.get())
            volume = max(0, min(100, volume))
            
            presets = self.app.config.get_preset_volumes()
            if volume not in presets:
                presets.append(volume)
                presets.sort()
                self.app.config.set_preset_volumes(presets)
                self._update_preset_list()
                self.new_preset_var.set('')
                self.app.tray_icon.update_menu()
        except ValueError:
            messagebox.showerror('错误', '请输入有效的音量值(0-100)')
    
    def _remove_preset(self):
        """删除预设音量"""
        selection = self.preset_listbox.curselection()
        if selection:
            index = selection[0]
            presets = self.app.config.get_preset_volumes()
            if 0 <= index < len(presets):
                presets.pop(index)
                self.app.config.set_preset_volumes(presets)
                self._update_preset_list()
                self.app.tray_icon.update_menu()
    
    def _add_task(self):
        """添加或保存定时任务"""
        try:
            hour = int(self.task_hour_var.get())
            minute = int(self.task_minute_var.get())
            volume = int(self.task_volume_var.get())
            
            hour = max(0, min(23, hour))
            minute = max(0, min(59, minute))
            volume = max(0, min(100, volume))
            
            time_str = f'{hour:02d}:{minute:02d}'
            
            if self.editing_task_id >= 0:
                # 保存编辑
                self.app.config.update_scheduled_task(
                    self.editing_task_id, 
                    time=time_str, 
                    volume=volume
                )
                # 重置编辑状态
                self.editing_task_id = -1
                self.add_task_btn.config(text='添加')
            else:
                # 添加新任务
                self.app.config.add_scheduled_task(time_str, volume)
            
            self._update_task_list()
            self.app.reload_scheduler()
            
        except ValueError:
            messagebox.showerror('错误', '请输入有效的数值')
    
    def _remove_task(self):
        """删除定时任务"""
        selection = self.task_tree.selection()
        if selection:
            item = selection[0]
            tags = self.task_tree.item(item, 'tags')
            if tags:
                task_id = int(tags[0])
                self.app.config.remove_scheduled_task(task_id)
                self._update_task_list()
                self.app.reload_scheduler()
    
    def _toggle_task(self):
        """启用/禁用定时任务"""
        selection = self.task_tree.selection()
        if selection:
            item = selection[0]
            tags = self.task_tree.item(item, 'tags')
            if tags:
                task_id = int(tags[0])
                tasks = self.app.config.get_scheduled_tasks()
                for task in tasks:
                    if task.get('id') == task_id:
                        new_enabled = not task.get('enabled', True)
                        self.app.config.update_scheduled_task(task_id, enabled=new_enabled)
                        break
                self._update_task_list()
                self.app.reload_scheduler()
    
    def _on_task_double_click(self, event):
        """双击任务列表项"""
        # 获取双击的行
        item = self.task_tree.identify_row(event.y)
        if item:
            # 选中该行
            self.task_tree.selection_set(item)
            # 调用编辑功能
            self._edit_task()
    
    def _edit_task(self):
        """编辑定时任务 - 将选中任务的数据填充到输入框"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请先选择一个任务')
            return
        
        item = selection[0]
        tags = self.task_tree.item(item, 'tags')
        if not tags:
            return
        
        task_id = int(tags[0])
        tasks = self.app.config.get_scheduled_tasks()
        
        # 找到选中的任务
        selected_task = None
        for task in tasks:
            if task.get('id') == task_id:
                selected_task = task
                break
        
        if not selected_task:
            return
        
        # 将任务数据填充到输入框
        current_time = selected_task['time'].split(':')
        self.task_hour_var.set(current_time[0])
        self.task_minute_var.set(current_time[1])
        self.task_volume_var.set(str(selected_task['volume']))
        
        # 设置编辑状态
        self.editing_task_id = task_id
        self.add_task_btn.config(text='保存')
    
    def _on_auto_start_changed(self):
        """开机自启动状态改变"""
        from auto_start import AutoStartManager
        
        enabled = self.auto_start_var.get()
        self.app.config.set_auto_start(enabled)
        
        if enabled:
            if AutoStartManager.enable():
                logger.info("已启用开机自启动")
            else:
                self.auto_start_var.set(False)
                self.app.config.set_auto_start(False)
                messagebox.showerror('错误', '启用开机自启动失败')
        else:
            if AutoStartManager.disable():
                logger.info("已禁用开机自启动")
            else:
                messagebox.showerror('错误', '禁用开机自启动失败')
    
    def _save_config(self):
        """保存配置"""
        if self.app.config.save():
            messagebox.showinfo('成功', '设置已保存')
        else:
            messagebox.showerror('错误', '保存失败')
    
    def _on_close(self):
        """窗口关闭回调"""
        if self.app.config.get('minimize_to_tray', True):
            self.hide()
        else:
            self._on_exit()
    
    def _on_exit(self):
        """退出应用"""
        if messagebox.askyesno('确认', '确定要退出程序吗？'):
            self.app.exit_app()
    
    def show(self):
        """显示窗口"""
        if self.root is None:
            self.create_window()
        
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_visible = True
        self._update_ui()
    
    def hide(self):
        """隐藏窗口"""
        if self.root:
            self.root.withdraw()
            self.is_visible = False
    
    def run(self):
        """运行主循环"""
        if self.root is None:
            self.create_window()
        self.root.mainloop()
    
    def stop(self):
        """停止窗口"""
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
            self.is_visible = False
