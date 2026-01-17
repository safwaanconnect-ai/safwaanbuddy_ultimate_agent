#!/usr/bin/env python3
"""Example usage scripts for SafwaanBuddy Ultimate++."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def example_automation():
    """Example: Basic automation."""
    print("\n=== Example: Basic Automation ===")
    
    from safwaanbuddy.automation import ClickSystem, TypeSystem
    
    click = ClickSystem()
    typer = TypeSystem()
    
    print("Automation systems initialized")
    print("- Click system ready for OCR-based clicking")
    print("- Type system ready for human-like typing")
    
    # Example operations (commented out to avoid actual execution)
    # click.click_text("Login")
    # typer.type_text("hello@example.com", human_like=True)
    # typer.press_key('tab')
    # typer.type_text("password123", human_like=True)


def example_form_filling():
    """Example: Form filling with profiles."""
    print("\n=== Example: Form Filling ===")
    
    from safwaanbuddy.automation import FormFiller
    from safwaanbuddy.automation.form_filler import FormField
    
    filler = FormFiller()
    
    # Load personal profile
    if filler.load_profile("personal"):
        print("✓ Profile 'personal' loaded")
        
        # Define form fields
        fields = [
            FormField("name", "text", label="Full Name", required=True, profile_key="full_name"),
            FormField("email", "email", label="Email", required=True, profile_key="email"),
            FormField("phone", "tel", label="Phone", profile_key="phone")
        ]
        
        print(f"✓ Defined {len(fields)} form fields")
        print("Ready to fill forms automatically!")
    else:
        print("✗ Failed to load profile")


def example_document_generation():
    """Example: Generate documents."""
    print("\n=== Example: Document Generation ===")
    
    from safwaanbuddy.documents import WordGenerator, ExcelGenerator
    
    # Word document
    print("\nGenerating Word document...")
    doc = WordGenerator()
    if doc.create_document():
        doc.add_heading("Sample Report", level=1)
        doc.add_paragraph("This is a sample document created by SafwaanBuddy.")
        
        table_data = [
            ["Name", "Score"],
            ["Alice", "95"],
            ["Bob", "87"]
        ]
        doc.add_table(table_data, has_header=True)
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        if doc.save_document(output_dir / "sample_report.docx"):
            print("✓ Word document created: output/sample_report.docx")
    
    # Excel spreadsheet
    print("\nGenerating Excel spreadsheet...")
    excel = ExcelGenerator()
    if excel.create_workbook("Data"):
        data = [
            ["Product", "Price", "Quantity"],
            ["Item A", 10.99, 5],
            ["Item B", 15.50, 3]
        ]
        excel.write_data(data)
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        if excel.save_workbook(output_dir / "sample_data.xlsx"):
            print("✓ Excel spreadsheet created: output/sample_data.xlsx")


def example_web_automation():
    """Example: Web automation."""
    print("\n=== Example: Web Automation ===")
    
    from safwaanbuddy.web import BrowserController, SearchEngine
    
    browser = BrowserController()
    search = SearchEngine()
    
    print("Web automation initialized")
    print("- Browser controller ready (Chrome/Firefox/Edge)")
    print("- Search engine ready (Google/Bing/DuckDuckGo)")
    
    # Example operations (commented to avoid actual browser launch)
    # browser.start_browser("chrome")
    # search.search("Python automation tutorial")
    # browser.navigate("https://example.com")
    # browser.close_browser()


def example_profile_management():
    """Example: Profile management."""
    print("\n=== Example: Profile Management ===")
    
    from safwaanbuddy.profiles import ProfileManager
    
    manager = ProfileManager()
    
    # List available profiles
    profiles = manager.list_profiles()
    print(f"Available profiles: {profiles}")
    
    # Load a profile
    if profiles:
        profile = manager.load_profile(profiles[0])
        if profile:
            print(f"✓ Loaded profile: {profile.get('name')}")
            print(f"  - Full name: {profile.get('full_name')}")
            print(f"  - Email: {profile.get('email')}")


def example_plugins():
    """Example: Using plugins."""
    print("\n=== Example: Plugins ===")
    
    from safwaanbuddy.plugins import PluginLoader
    
    loader = PluginLoader()
    loader.load_plugins()
    
    plugins = list(loader.plugins.keys())
    print(f"Loaded plugins: {plugins}")
    
    # Example: Use calculator plugin
    if "Calculator" in plugins:
        result = loader.execute_plugin("Calculator", "2 + 2 * 5")
        print(f"Calculator result: 2 + 2 * 5 = {result}")
    
    # Example: Use notes plugin
    if "Notes" in plugins:
        result = loader.execute_plugin("Notes", "list")
        print(f"Notes: {result}")


def example_monitoring():
    """Example: System monitoring."""
    print("\n=== Example: System Monitoring ===")
    
    from safwaanbuddy.utils import SystemMonitor
    
    monitor = SystemMonitor()
    
    # Get system info
    info = monitor.get_system_info()
    
    print(f"CPU Usage: {info['cpu']['usage']:.1f}%")
    print(f"CPU Cores: {info['cpu']['count']}")
    print(f"Memory Used: {info['memory']['used']:.1f} GB / {info['memory']['total']:.1f} GB ({info['memory']['percent']:.1f}%)")
    print(f"Disk Used: {info['disk']['used']:.1f} GB / {info['disk']['total']:.1f} GB ({info['disk']['percent']:.1f}%)")


def example_event_system():
    """Example: Event system."""
    print("\n=== Example: Event System ===")
    
    from safwaanbuddy.core import EventBus, EventType
    
    event_bus = EventBus()
    
    # Subscribe to events
    def on_info_message(event):
        print(f"  [EVENT] Info: {event.data.get('message')}")
    
    event_bus.subscribe(EventType.INFO_MESSAGE, on_info_message)
    
    # Emit event
    print("Emitting test event...")
    event_bus.emit(EventType.INFO_MESSAGE, {"message": "Hello from SafwaanBuddy!"})
    
    print("✓ Event system working")


def main():
    """Run all examples."""
    print("=" * 60)
    print("SafwaanBuddy Ultimate++ v7.0 - Usage Examples")
    print("=" * 60)
    
    examples = [
        ("Automation", example_automation),
        ("Form Filling", example_form_filling),
        ("Document Generation", example_document_generation),
        ("Web Automation", example_web_automation),
        ("Profile Management", example_profile_management),
        ("Plugins", example_plugins),
        ("System Monitoring", example_monitoring),
        ("Event System", example_event_system)
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n✗ {name} example failed: {e}")
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
