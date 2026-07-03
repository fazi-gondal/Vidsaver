import os
import re
import threading
import requests
import flet as ft
import flet_video as ftv  # Dedicated video playback extension
import flet_permission_handler as fph  # Separate extension package — not part of core flet
from yt_dlp import YoutubeDL

ANDROID_STORAGE_ROOT = "/storage/emulated/0"


async def main(page: ft.Page):
    page.title = "Universal Video Hub"
    page.window.maximized = True
    page.padding=0
    page.spacing=0
    page.safe_area=True
    is_mobile = page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
    if is_mobile:
        page.appbar=ft.AppBar(title=ft.Text("Universal Video Hub"),center_title=True)
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    url_input_focused = False
    page_max_height = page.height or 0

    async def handle_page_resize(e):
        nonlocal page_max_height
        if page.height and page.height > page_max_height:
            page_max_height = page.height
        if url_input_focused and page.height and page.height >= page_max_height:
            try:
                await download_btn.focus()
            except Exception:
                pass

    page.on_resize = handle_page_resize

    is_android = os.path.exists(ANDROID_STORAGE_ROOT)

    # ------------------ ANDROID STORAGE PERMISSION ------------------
    # Since this app is sideloaded (not on Play Store), MANAGE_EXTERNAL_STORAGE
    # ("All files access") is the simplest reliable option — it bypasses scoped
    # storage entirely, so the existing raw-path yt-dlp write below just works.
    # It must also be declared in pyproject.toml:
    #   [tool.flet.android.permission]
    #   "android.permission.MANAGE_EXTERNAL_STORAGE" = true
    permission_handler = fph.PermissionHandler()
    page.services.append(permission_handler)  # PermissionHandler is a Service, not an overlay control

    async def has_storage_access() -> bool:
        if not is_android:
            return True
        try:
            status = await permission_handler.get_status(fph.Permission.MANAGE_EXTERNAL_STORAGE)
        except Exception:
            return False
        return status == fph.PermissionStatus.GRANTED

    async def request_storage_access(e=None):
        if not is_android:
            return
        # This routes to the special system settings screen ("Allow management
        # of all files") — the toggle has to be flipped manually by the user,
        # there's no silent/instant grant for this particular permission.
        try:
            await permission_handler.request(fph.Permission.MANAGE_EXTERNAL_STORAGE)
        except Exception:
            pass
        if await has_storage_access():
            grant_access_btn.visible = False
            status_text.value = "Storage access granted. Ready to download!"
        else:
            status_text.value = (
                "Enable 'Allow management of all files' for this app in the "
                "settings screen that just opened, then come back here."
            )
        page.update()

    # 📂 PERMANENT DYNAMIC PATH EVALUATION:
    if is_android:
        # Movies/ is one of the standard public directories Android's MediaProvider
        # actively watches and indexes into the Video collection — files saved here
        # show up in Gallery apps and video players automatically. Download/ isn't
        # consistently indexed the same way across OEM skins.
        download_dir = os.path.join(ANDROID_STORAGE_ROOT, "Movies", "VidSaver")
    else:
        try:
            sp = ft.StoragePaths(page)
            download_dir = await sp.get_downloads_directory() or "./downloads"
        except Exception:
            download_dir = os.path.join(os.environ['USERPROFILE'], 'Downloads') if 'USERPROFILE' in os.environ else "./downloads"

    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)

    # ------------------ TAB 1: DOWNLOADER UI ELEMENTS ------------------
    def on_url_focus(e):
        nonlocal url_input_focused
        url_input_focused = True
        if page.navigation_bar:
            page.navigation_bar.visible = False
            page.update()

    def on_url_blur(e):
        nonlocal url_input_focused
        url_input_focused = False
        if page.navigation_bar and main_container.content != player_view:
            page.navigation_bar.visible = True
            page.update()

    url_input = ft.TextField(
        label="Paste Social Media Video Link",
        width=400,
        on_focus=on_url_focus,
        on_blur=on_url_blur,
    )
    status_text = ft.Text(value="Ready", color=ft.Colors.BLUE_GREY)
    progress_bar = ft.ProgressBar(width=400, value=0.0, visible=False, color=ft.Colors.BLUE)

    def clean_ansi(text):
        return re.sub(r'\x1b\[[0-9;]*[mGKH]', '', text)

    def ytdl_hook(d):
        if d['status'] == 'downloading':
            raw_percent = d.get('_percent_str', '0%')
            clean_percent = clean_ansi(raw_percent).replace('%', '').strip()
            try:
                float_val = float(clean_percent) / 100.0
                progress_bar.value = float_val
            except ValueError:
                pass
            status_text.value = f"Downloading: {raw_percent.strip()}"
            page.update()
        elif d['status'] == 'finished':
            progress_bar.value = 1.0
            status_text.value = "Saving file..."
            page.update()

    def resolve_short_url(url):
        if "tiktok.com" in url:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            try:
                response = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
                return response.url
            except Exception:
                return url
        return url

    def download_video(url, target_dir):
        final_url = resolve_short_url(url)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cookie_path = os.path.join(base_dir, 'cookies.txt')

        if not os.path.exists(cookie_path):
            status_text.value = "Error: 'cookies.txt' file missing!"
            progress_bar.visible = False
            page.update()
            return

        ydl_opts = {
            'outtmpl': os.path.join(target_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [ytdl_hook],
            'cookiefile': cookie_path, 
            'format': 'best[ext=mp4]/best', 
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([final_url])
            status_text.value = "Success! Video saved successfully."
            refresh_downloads_list()
        except Exception as e:
            status_text.value = f"Network Timeout / Blocked.\n{str(e)}"
        finally:
            progress_bar.visible = False
            page.update()

    async def on_download_click(e):
        try:
            await download_btn.focus()
        except Exception:
            pass
        if not url_input.value:
            status_text.value = "Please enter a valid URL!"
            page.update()
            return

        if not await has_storage_access():
            grant_access_btn.visible = True
            status_text.value = "Storage access needed — tap 'Grant Storage Access' first."
            page.update()
            return

        progress_bar.value = 0.0
        progress_bar.visible = True
        status_text.value = "Unwrapping short-link and connecting..."
        page.update()
        
        threading.Thread(target=download_video, args=(url_input.value, download_dir), daemon=True).start()

    download_btn = ft.Button("Download Video", on_click=on_download_click)

    async def on_url_submit(e):
        try:
            await download_btn.focus()
        except Exception:
            pass
        await on_download_click(e)

    url_input.on_submit = on_url_submit
    grant_access_btn = ft.Button(
        "Grant Storage Access",
        on_click=request_storage_access,
        visible=False,
        icon=ft.Icons.FOLDER_OPEN,
    )

    home_view = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Media Downloader", size=24, weight=ft.FontWeight.BOLD),
                    url_input,
                    download_btn,
                    grant_access_btn,
                    progress_bar,
                    status_text
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            padding=30
        )
    )
    # ------------------ TAB 2: DOWNLOADS STORAGE LISTVIEW ------------------
    downloads_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    
    # 🌟 FIXED: Create player control inside a permanent main widget tree node
    video_player_control = ftv.Video(expand=True, autoplay=True)
    player_title = ft.Text(value="", weight=ft.FontWeight.BOLD, size=16)

    async def close_player(e):
        # Swap back to the library view structure FIRST so the transition
        # feels instant. Pausing media_kit's native player can take a beat
        # to round-trip, so we don't want the screen swap waiting on it.
        main_container.content = library_view
        main_container.alignment = None  # library also relies on an expand=True chain
        page.navigation_bar.visible = True
        page.update()
        try:
            await video_player_control.pause()
        except Exception:
            pass

    video_player_control.on_complete = close_player

    # 🌟 FIXED: Created an explicit Full-Screen Player interface view layout
    player_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        player_title,
                        ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_player, icon_color=ft.Colors.RED)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                # This wraps the player video control frame securely
                ft.Container(
                    content=video_player_control,
                    expand=True,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                )
            ],
            expand=True
        ),
        padding=15,
        expand=True
    )

    def play_video(file_name):
        full_path = os.path.join(download_dir, file_name)
        player_title.value = file_name
        
        # Link the file to the playlist
        video_player_control.playlist = [ftv.VideoMedia(full_path)]
        
        # 🌟 FIXED: Dynamically inject the full player screen over the container context node
        main_container.content = player_view
        # IMPORTANT: main_container.alignment=CENTER (used to center the Home card)
        # wraps its child in an Align widget, which gives the child *loose*
        # constraints and collapses any expand=True chain underneath it to
        # zero size. That's why the video was blank but audio still played.
        # Clear it whenever we're not showing the Home view.
        main_container.alignment = None
        page.navigation_bar.visible = False  # Hide nav tabs while watching the media track
        page.update()
        video_player_control.update()

    def delete_file(file_name):
        full_path = os.path.join(download_dir, file_name)
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                page.overlay.append(ft.SnackBar(ft.Text(f"Deleted from device: {file_name}"), open=True))
            else:
                page.overlay.append(ft.SnackBar(ft.Text("File already removed from device."), open=True))
            refresh_downloads_list()
        except Exception as ex:
            page.overlay.append(ft.SnackBar(ft.Text(f"Permission Error: {str(ex)}"), open=True))
            page.update()

    def refresh_downloads_list():
        downloads_list_view.controls.clear()
        try:
            files = [f for f in os.listdir(download_dir) if f.lower().endswith(('.mp4', '.mkv', '.mov', '.avi'))]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)
            
            if not files:
                downloads_list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.FOLDER_OPEN, color=ft.Colors.GREY),
                        title=ft.Text("No downloaded videos found yet.", color=ft.Colors.GREY)
                    )
                )
            else:
                for file_name in files:
                    downloads_list_view.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.VIDEO_FILE, color=ft.Colors.BLUE),
                            title=ft.Text(file_name, size=14, weight=ft.FontWeight.W_500),
                            subtitle=ft.Text(f"Path: {download_dir}", size=11, color=ft.Colors.GREY_500),
                            on_click=lambda e, filename=file_name: play_video(filename),
                            trailing=ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                tooltip="Delete Video From Device",
                                on_click=lambda e, filename=file_name: delete_file(filename)
                            )
                        )
                    )
        except Exception as e:
            downloads_list_view.controls.append(ft.Text(f"Failed to index files: {str(e)}", color=ft.Colors.RED))
        
        page.update()

    library_view = ft.Column(
        controls=[
            ft.Text("Your Downloads", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Directory: {download_dir}", size=12, color=ft.Colors.BLUE_GREY),
            ft.Divider(),
            downloads_list_view
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )

    # Reflect current storage-permission state before the app is first shown
    if is_android and not await has_storage_access():
        grant_access_btn.visible = True
        status_text.value = "Storage access needed — tap 'Grant Storage Access' below."

    # ------------------ CORE APPLICATION ROUTER SETUP ------------------
    def on_container_click(e):
        pass  # Will be defined as async below

    async def on_container_click_async(e):
        if main_container.content == home_view:
            try:
                await download_btn.focus()
            except Exception:
                pass

    main_container = ft.Container(
        content=home_view,
        expand=True,
        alignment=ft.Alignment.CENTER,
        on_click=on_container_click_async
    )

    async def on_navigation_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            home_view.visible = True
            library_view.visible = False
            main_container.content = home_view
            main_container.alignment = ft.Alignment.CENTER  # safe to center: Card doesn't need expand
            page.update()  # swap screens immediately, don't wait on pause()
            try:
                await video_player_control.pause()
            except Exception:
                pass
        elif selected_index == 1:
            refresh_downloads_list()
            home_view.visible = False
            library_view.visible = True
            main_container.content = library_view
            main_container.alignment = None  # let the expand=True list fill the screen
            page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.DOWNLOAD, label="Downloads"),
        ]
    )

    page.add(ft.SafeArea(content=main_container, expand=True))

ft.run(main)