import asyncio
import random
import time
import uuid
import urllib.parse
from playwright.async_api import async_playwright

try:
    from playwright_stealth import Stealth
except ImportError:
    Stealth = None

# ==========================================
# PAHLE WALE SCRIPT KE PROXIES
# ==========================================
PROXY_LIST = {
    # NL Residential
    "it": "http://cv3cka1ebn-pool-res-country-IT-mode-query:bX0wu8xXZSnDYn6G@93.190.141.105:9999",
    # US Mobile
    "ch": "http://cv3cka1ebn-pool-mobile-country-CH-mode-query:bX0wu8xXZSnDYn6G@89.38.99.96:9999",
    "it": "http://cv3cka1ebn-pool-mobile-country-IT-mode-query:bX0wu8xXZSnDYn6G@109.236.84.23:9999",
    
}

TARGET_DOMAIN = "tooliyapooliya.blogspot.com"
MAX_SLOTS = 3

GEO_DATA = {
    "us": {
        "tz": "America/New_York",
        "lang": ["en-US", "en"],
        "geo": {"latitude": 40.7128, "longitude": -74.0060},
    },
    "nl": {
        "tz": "Europe/Amsterdam",
        "lang": ["nl-NL", "nl", "en"],
        "geo": {"latitude": 52.3676, "longitude": 4.9041},
    },
    "ca": {
        "tz": "America/Toronto",
        "lang": ["en-CA", "fr-CA", "en"],
        "geo": {"latitude": 43.6532, "longitude": -79.3832},
    },
    "de": {
        "tz": "Europe/Berlin",
        "lang": ["de-DE", "de", "en"],
        "geo": {"latitude": 52.5200, "longitude": 13.4050},
    },
    "fr": {
        "tz": "Europe/Paris",
        "lang": ["fr-FR", "fr", "en"],
        "geo": {"latitude": 48.8566, "longitude": 2.3522},
    },
    "gb": {
        "tz": "Europe/London",
        "lang": ["en-GB", "en"],
        "geo": {"latitude": 51.5074, "longitude": -0.1278},
    },
    "uk": {
        "tz": "Europe/London",
        "lang": ["en-GB", "en"],
        "geo": {"latitude": 51.5074, "longitude": -0.1278},
    },
    "gr": {
        "tz": "Europe/Athens",
        "lang": ["el-GR", "el", "en"],
        "geo": {"latitude": 37.9838, "longitude": 23.7275},
    },
    "ch": {
        "tz": "Europe/Zurich",
        "lang": ["de-CH", "fr-CH", "it-CH", "en"],
        "geo": {"latitude": 47.3769, "longitude": 8.5417},
    },
    "ru": {
        "tz": "Europe/Moscow",
        "lang": ["ru-RU", "ru", "en"],
        "geo": {"latitude": 55.7558, "longitude": 37.6173},
    },
    "it": {
        "tz": "Europe/Rome",
        "lang": ["it-IT", "it", "en"],
        "geo": {"latitude": 41.9028, "longitude": 12.4964},
    },
    "br": {
        "tz": "America/Sao_Paulo",
        "lang": ["pt-BR", "pt", "en"],
        "geo": {"latitude": -23.5505, "longitude": -46.6333},
    },
    "au": {
        "tz": "Australia/Sydney",
        "lang": ["en-AU", "en"],
        "geo": {"latitude": -33.8688, "longitude": 151.2093},
    },
    "se": {
        "tz": "Europe/Stockholm",
        "lang": ["sv-SE", "sv", "en"],
        "geo": {"latitude": 59.3293, "longitude": 18.0686},
    },
    "es": {
        "tz": "Europe/Madrid",
        "lang": ["es-ES", "es", "en"],
        "geo": {"latitude": 40.4168, "longitude": -3.7038},
    },
    "jp": {
        "tz": "Asia/Tokyo",
        "lang": ["ja-JP", "ja", "en"],
        "geo": {"latitude": 35.6762, "longitude": 139.6503},
    },
    "in": {
        "tz": "Asia/Kolkata",
        "lang": ["hi-IN", "en-IN", "en"],
        "geo": {"latitude": 28.6139, "longitude": 77.2090},
    },
    "sg": {
        "tz": "Asia/Singapore",
        "lang": ["en-SG", "zh-SG", "en"],
        "geo": {"latitude": 1.3521, "longitude": 103.8198},
    },
    "ae": {
        "tz": "Asia/Dubai",
        "lang": ["ar-AE", "en-AE", "en"],
        "geo": {"latitude": 25.2048, "longitude": 55.2708},
    },
    "pl": {
        "tz": "Europe/Warsaw",
        "lang": ["pl-PL", "pl", "en"],
        "geo": {"latitude": 52.2297, "longitude": 21.0122},
    },
    "tr": {
        "tz": "Europe/Istanbul",
        "lang": ["tr-TR", "tr", "en"],
        "geo": {"latitude": 41.0082, "longitude": 28.9784},
    },
}
DEFAULT_GEO = GEO_DATA["us"]


def build_proxy_config(proxy_url):
    if not proxy_url:
        return None
    parsed = urllib.parse.urlparse(proxy_url)
    if not parsed.hostname or not parsed.port:
        return None
    cfg = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
    if parsed.username:
        cfg["username"] = parsed.username
    if parsed.password:
        cfg["password"] = parsed.password
    return cfg


def generate_fingerprint(country_code, is_mobile_proxy):
    geo = GEO_DATA.get(country_code, DEFAULT_GEO)
    major = random.randint(122, 130)
    build = random.randint(1000, 6000)
    patch = random.randint(10, 150)

    if is_mobile_proxy:
        os_type = random.choice(["android", "ios"])
        if os_type == "android":
            ua = (
                f"Mozilla/5.0 (Linux; Android {random.randint(12, 14)}; SM-S918B) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{major}.0.{build}.{patch} Mobile Safari/537.36"
            )
            viewport = {"width": 412, "height": 915}
        else:
            ua = (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.5 Mobile/15E148 Safari/604.1"
            )
            viewport = {"width": 390, "height": 844}
        is_mobile = True
    else:
        is_mobile = random.random() < 0.3
        if is_mobile:
            ua = (
                f"Mozilla/5.0 (Linux; Android {random.randint(12, 14)}; Pixel 7) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{major}.0.{build}.{patch} Mobile Safari/537.36"
            )
            viewport = {"width": 412, "height": 915}
        else:
            os_type = random.choices(["win", "mac", "linux"], weights=[0.6, 0.3, 0.1])[0]
            if os_type == "win":
                ua = (
                    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    f"AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{major}.0.{build}.{patch} Safari/537.36"
                )
            elif os_type == "mac":
                ua = (
                    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    f"AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{major}.0.{build}.{patch} Safari/537.36"
                )
            else:
                ua = (
                    f"Mozilla/5.0 (X11; Linux x86_64) "
                    f"AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{major}.0.{build}.{patch} Safari/537.36"
                )
            screens = [
                {"width": 1366, "height": 768},
                {"width": 1536, "height": 864},
                {"width": 1440, "height": 900},
            ]
            viewport = random.choice(screens)

    return {
        "user_agent": ua,
        "viewport": viewport,
        "is_mobile": is_mobile,
        "timezone_id": geo["tz"],
        "locale": geo["lang"][0],
        "geolocation": geo["geo"],
    }


class HumanBehavior:
    @staticmethod
    async def bezier_mouse_move(page, start_x, start_y, end_x, end_y):
        steps = random.randint(20, 40)
        control_x = (start_x + end_x) / 2 + random.randint(-100, 100)
        control_y = (start_y + end_y) / 2 + random.randint(-100, 100)
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t**2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t**2 * end_y
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.005, 0.015))

    @staticmethod
    async def human_scroll(page, duration_sec, reading_speed="normal"):
        end_time = time.time() + duration_sec
        while time.time() < end_time:
            direction = 1 if random.random() < 0.8 else -1
            if reading_speed == "fast":
                amount = random.randint(280, 550)
            elif reading_speed == "slow":
                amount = random.randint(60, 160)
            else:
                amount = random.randint(150, 350)

            await page.mouse.wheel(0, amount * direction)

            if random.random() < 0.4:
                await asyncio.sleep(random.uniform(1.8, 4.5))
            else:
                await asyncio.sleep(random.uniform(0.5, 1.5))


async def safe_navigate(page, url, session_id, referer=""):
    try:
        print(f"[{session_id}] Loading blog...")
        if referer:
            await page.goto(url, timeout=80000, wait_until="domcontentloaded", referer=referer)
        else:
            await page.goto(url, timeout=80000, wait_until="domcontentloaded")

        await asyncio.sleep(random.uniform(2, 4))

        content = await page.content()
        if "Just a moment" in content or "Attention Required" in content or "cf-challenge" in content:
            print(f"[{session_id}] Challenge / captcha page detected.")
            return False
        return True
    except Exception as e:
        print(f"[{session_id}] Nav Error: {e}")
        return False


async def click_random_post(page, session_id, viewport, current_pos):
    try:
        links = await page.locator("a.post-title, h2.post-title a, article a, .post-outer a").all()
        valid_links = []
        for link in links:
            href = await link.get_attribute("href")
            if href and TARGET_DOMAIN in href and not href.startswith("#"):
                box = await link.bounding_box()
                if box and box["width"] > 5 and box["height"] > 5:
                    valid_links.append((link, box))

        if not valid_links:
            return False

        target_link, box = random.choice(valid_links)
        await target_link.scroll_into_view_if_needed(timeout=5000)
        box = await target_link.bounding_box()
        if not box:
            return False

        start_x, start_y = current_pos
        target_x = min(max(10, box["x"] + box["width"] / 2), viewport["width"] - 10)
        target_y = min(max(10, box["y"] + box["height"] / 2), viewport["height"] - 10)

        await HumanBehavior.bezier_mouse_move(page, start_x, start_y, target_x, target_y)
        current_pos[0], current_pos[1] = target_x, target_y
        await asyncio.sleep(random.uniform(0.2, 0.5))

        await target_link.click()
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        await asyncio.sleep(random.uniform(1.5, 3.0))
        print(f"[{session_id}] Clicked on a post.")
        return True
    except Exception:
        return False


async def run_tab_session(slot_id, available_countries):
    session_id = f"S-{str(uuid.uuid4())[:6]}"
    country = random.choice(available_countries)
    proxy_url = PROXY_LIST[country]
    is_mobile_proxy = "-mobile-" in proxy_url.lower()
    proxy_config = build_proxy_config(proxy_url)
    geo_info = generate_fingerprint(country, is_mobile_proxy)

    print(
        f"[Slot-{slot_id}] Start {session_id} | Country: {country.upper()} | Mobile: {is_mobile_proxy}"
    )

    browser = None
    context = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process",
                ],
            )

            context_kwargs = {
                "user_agent": geo_info["user_agent"],
                "viewport": geo_info["viewport"],
                "is_mobile": geo_info["is_mobile"],
                "has_touch": geo_info["is_mobile"],
                "timezone_id": geo_info["timezone_id"],
                "locale": geo_info["locale"],
                "geolocation": geo_info["geolocation"],
                "permissions": ["geolocation"],
            }
            if proxy_config:
                context_kwargs["proxy"] = proxy_config

            context = await browser.new_context(**context_kwargs)

            if Stealth is not None:
                await Stealth().apply_stealth_async(context)

            page = await context.new_page()

            # Sab kuch render karwane ke liye koi block rule nahi lagaya gaya hai
            await page.route("**/*", lambda route: route.continue_())

            referrer = random.choice(["https://www.google.com/", "https://www.facebook.com/", ""])
            entry_url = f"https://{TARGET_DOMAIN}"

            if not await safe_navigate(page, entry_url, session_id, referer=referrer):
                return

            duration = random.randint(40, 180)
            reading_speed = random.choice(["fast", "normal", "slow"])
            print(f"[Slot-{slot_id}] {session_id} active for {duration}s (Reader: {reading_speed})")

            loop_end = time.time() + duration
            depth = 0
            vp = geo_info["viewport"]
            current_pos = [
                random.randint(60, max(70, vp["width"] - 60)),
                random.randint(100, max(120, vp["height"] - 100)),
            ]

            while time.time() < loop_end:
                if random.random() < 0.2:
                    print(f"[Slot-{slot_id}] {session_id} bounced.")
                    break

                await HumanBehavior.human_scroll(page, random.randint(4, 9), reading_speed)

                target_x = random.randint(50, max(60, vp["width"] - 50))
                target_y = random.randint(100, max(120, vp["height"] - 100))
                await HumanBehavior.bezier_mouse_move(
                    page, current_pos[0], current_pos[1], target_x, target_y
                )
                current_pos[0], current_pos[1] = target_x, target_y

                if depth < 2 and random.random() < 0.4:
                    if await click_random_post(page, session_id, vp, current_pos):
                        depth += 1
                        await HumanBehavior.human_scroll(page, random.randint(4, 9), reading_speed)
                        if random.random() < 0.3:
                            try:
                                await page.go_back(wait_until="domcontentloaded", timeout=25000)
                                await asyncio.sleep(random.uniform(1.5, 3.0))
                            except Exception:
                                pass

            print(f"[Slot-{slot_id}] {session_id} ended.")

    except Exception as e:
        print(f"[Slot-{slot_id}] [!] Error: {e}")
    finally:
        if context:
            try:
                await context.close()
            except Exception:
                pass
        if browser:
            try:
                await browser.close()
            except Exception:
                pass


async def supervisor():
    available_countries = list(PROXY_LIST.keys())
    slots = asyncio.Queue()
    for i in range(1, MAX_SLOTS + 1):
        slots.put_nowait(i)

    active_tasks = set()
    while True:
        slot_id = await slots.get()
        task = asyncio.create_task(run_tab_session(slot_id, available_countries))
        active_tasks.add(task)

        def _on_done(t, s_id=slot_id):
            active_tasks.discard(t)
            slots.put_nowait(s_id)

        task.add_done_callback(_on_done)
        await asyncio.sleep(random.uniform(0, 3))


if __name__ == "__main__":
    print("Starting Improved Visual Human Traffic Engine...")
    asyncio.run(supervisor())
    
