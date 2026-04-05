from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Button, DataTable, Select, Switch, Sparkline, ProgressBar
from textual.screen import Screen
from textual import on, work
from loguru import logger
import httpx
import os
import asyncio
from typing import Optional

from src.security.auth import authenticate_user, AuthenticationError
from src.security.audit import get_recent_audit_logs, log_audit_event
from src.ingestion.manager import IngestionManager
from src.prompts.loader import prompt_loader
from src.prompts.watcher import prompt_watcher
from src.orchestration.ab_engine import ab_engine, ABConfig
from src.security.vault import vault_service
from src.security.guardrails import guardrail_service
from src.orchestration.models import ValidationReport

class LoginScreen(Screen):
    """A screen for user authentication."""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Local LLM Assistant - Secure Login", id="login-title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Button("Login", variant="primary", id="login-btn"),
            Static("", id="error-msg"),
            id="login-container"
        )

    @on(Button.Pressed, "#login-btn")
    def handle_login(self) -> None:
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value
        error_msg = self.query_one("#error-msg", Static)
        
        try:
            session = authenticate_user(username, password)
            self.app.user_session = session
            self.app.push_screen(MainDashboard())
        except AuthenticationError as e:
            error_msg.update(f"[red]{str(e)}[/red]")

class MainDashboard(Screen):
    """The main application dashboard with A/B Testing support."""
    current_test_id = None

    def compose(self) -> ComposeResult:
        supported_models = os.getenv("SUPPORTED_MODELS", "phi3:mini,tinyllama").split(",")
        model_options = [(m.strip(), m.strip()) for m in supported_models]
        default_model = os.getenv("DEFAULT_MODEL", "phi3:mini")

        yield Header()
        yield Horizontal(
            Vertical(
                Static("Secure Chat & Ingestion", classes="pane-title"),
                
                # Dynamic area for single or dual chat
                Container(
                    Vertical(Static(id="chat-area-a"), id="pane-a"),
                    Vertical(Static(id="chat-area-b"), id="pane-b", classes="hidden"),
                    id="chat-container"
                ),

                Horizontal(
                    Button("Vote A", id="vote-a", variant="success", classes="hidden"),
                    Button("Vote B", id="vote-b", variant="success", classes="hidden"),
                    id="vote-bar"
                ),

                Horizontal(
                    Input(placeholder="File Path (PDF/TXT/CSV)...", id="file-input"),
                    Button("Ingest", id="ingest-btn"),
                    id="ingest-bar"
                ),
                Input(placeholder="Ask anything...", id="chat-input"),
                id="left-pane"
            ),
            Vertical(
                Static("System Control & Metrics", classes="pane-title"),
                Static(f"User: [bold cyan]{self.app.user_session.username}[/bold cyan]"),
                
                # Model Controls
                Static("Primary Model (Config A):", classes="sub-title"),
                Select(model_options, value=default_model, id="model-select-a"),
                Select([], id="prompt-select-a"),
                
                Horizontal(
                    Static("PII Masking"), Switch(value=True, id="masking-toggle"),
                    Static("Vault Guard"), Switch(value=False, id="vault-toggle"),
                    classes="toggle-row"
                ),
                Horizontal(
                    Static("Dual Mode (A/B)"), Switch(value=False, id="dual-toggle"),
                    classes="toggle-row"
                ),

                Container(
                    Static("Config B (Comparison):", classes="sub-title"),
                    Select(model_options, value=supported_models[-1].strip(), id="model-select-b"),
                    Select([], id="prompt-select-b"),
                    id="config-b-container",
                    classes="hidden"
                ),

                # Real-time Metrics
                Static("Throughput & Latency", classes="sub-title"),
                Vertical(
                    Static("Latency (ms)"),
                    Sparkline(data=[], id="latency-sparkline", classes="sparkline"),
                    Static("Tokens/sec"),
                    Sparkline(data=[], id="tps-sparkline", classes="sparkline"),
                    classes="metric-box"
                ),

                Static("Privacy & Security Stats", classes="sub-title"),
                Vertical(
                    Static("PII Redactions"),
                    Sparkline(data=[], id="pii-sparkline", classes="sparkline"),
                    classes="metric-box"
                ),

                Static("Security Audit", classes="sub-title"),
                DataTable(id="audit-table"),
                
                id="right-pane"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        self.latency_history = []
        self.tps_history = []
        self.refresh_prompts()
        self.update_dashboard()
        self.set_interval(3.0, self.update_dashboard)
        prompt_watcher.add_callback(self.refresh_prompts)

    def update_dashboard(self) -> None:
        """Polls SQL metrics and updates sparklines/tables."""
        # 1. Update Audit Log
        table = self.query_one("#audit-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Time", "User", "Action", "Status")
        logs = get_recent_audit_logs(limit=8)
        for log in logs:
            table.add_row(*log)

        # 2. Update Performance Sparklines
        # We query the metrics table for recent generation data
        import sqlcipher3 as sqlite3
        db_path = os.getenv("DB_PATH", "data/secure_vault.db")
        db_key = os.getenv("DB_ENCRYPTION_KEY", "default-insecure-key")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.execute(f"PRAGMA key = '{db_key}';")
            cursor = conn.cursor()
            cursor.execute("SELECT latency_ms, tokens_per_sec, redacted_count FROM metrics ORDER BY timestamp DESC LIMIT 20")
            rows = cursor.fetchall()
            conn.close()

            if rows:
                # Extract values and reverse to chronological order
                latencies = [r[0] for r in rows][::-1]
                tps = [r[1] for r in rows][::-1]
                pii_counts = [r[2] for r in rows][::-1]
                
                self.query_one("#latency-sparkline", Sparkline).data = latencies
                self.query_one("#tps-sparkline", Sparkline).data = tps
                self.query_one("#pii-sparkline", Sparkline).data = pii_counts
        except Exception as e:
            logger.error(f"Dashboard poll failed: {e}")

    def refresh_prompts(self) -> None:
        """Reloads the prompt list for both selectors."""
        available = prompt_loader.list_prompts()
        logger.info(f"TUI Refreshing prompts. Found: {len(available)} templates.")
        options = [(f"{p['id']} (v{p['version']})", p['id']) for p in available]
        
        for suffix in ["a", "b"]:
            select = self.query_one(f"#prompt-select-{suffix}", Select)
            select.set_options(options)
            if options:
                select.value = options[0][1]
                logger.info(f"Set prompt-select-{suffix} value to: {select.value}")

    def update_audit_log(self) -> None:
        table = self.query_one("#audit-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Time", "User", "Action", "Status")
        logs = get_recent_audit_logs(limit=10)
        for log in logs:
            table.add_row(*log)

    @on(Switch.Changed, "#dual-toggle")
    def toggle_dual_mode(self, event: Switch.Changed) -> None:
        """Shows/Hides dual panes based on toggle."""
        dual_mode = event.value
        self.query_one("#pane-b").set_class(not dual_mode, "hidden")
        self.query_one("#config-b-container").set_class(not dual_mode, "hidden")
        self.query_one("#chat-container").set_class(dual_mode, "side-by-side")
        
        # Reset voting bar
        self.query_one("#vote-a").add_class("hidden")
        self.query_one("#vote-b").add_class("hidden")

    @on(Button.Pressed, "#ingest-btn")
    def handle_ingestion(self) -> None:
        file_path = self.query_one("#file-input", Input).value
        masking_enabled = self.query_one("#masking-toggle", Switch).value
        dual_mode = self.query_one("#dual-toggle", Switch).value
        
        if not file_path:
            self.query_one("#chat-area-a", Static).update("[red]Please enter a file path.[/red]")
            return
            
        self.process_request(file_path, is_file=True)

    @on(Input.Submitted, "#chat-input")
    def handle_chat(self, event: Input.Submitted) -> None:
        query = event.value
        if not query:
            return
        self.process_request(query, is_file=False)
        self.query_one("#chat-input", Input).value = ""

    @work(exclusive=True)
    async def process_request(self, content: str, is_file: bool) -> None:
        """Async processing of single or dual requests."""
        masking_enabled = self.query_one("#masking-toggle", Switch).value
        vault_enabled = self.query_one("#vault-toggle", Switch).value
        dual_mode = self.query_one("#dual-toggle", Switch).value
        
        area_a = self.query_one("#chat-area-a", Static)
        area_b = self.query_one("#chat-area-b", Static)
        
        area_a.update("[bold yellow]Processing...[/bold yellow]")
        if dual_mode:
            area_b.update("[bold yellow]Processing...[/bold yellow]")

        try:
            # 1. Prepare data (Ingest if file)
            user_id = self.app.user_session.user_id
            redacted_count = 0
            if is_file:
                manager = IngestionManager(use_masking=masking_enabled)
                text_to_process, redacted_count = manager.process_file(content, user_id=user_id)
                # Save to Vault if enabled
                if vault_enabled:
                    vault_service.save_to_vault(user_id, os.path.basename(content), text_to_process)
                    area_a.update(f"[green]File vaulted: {os.path.basename(content)}[/green]\nProcessing...")
            else:
                text_to_process = content
                if masking_enabled:
                    text_to_process, redacted_count = masking_service.mask_text(content)

            # 2. Setup Configs
            prompt_obj_a = prompt_loader.get_prompt(str(self.query_one("#prompt-select-a", Select).value))
            prompt_obj_b = prompt_loader.get_prompt(str(self.query_one("#prompt-select-b", Select).value))
            
            # Determine what goes into the template
            query_val = content if not is_file else "Summarize the following document and identify key points."
            content_val = text_to_process if is_file else ""
            
            rendered_a = prompt_obj_a.render(query=query_val, content=content_val)
            rendered_b = prompt_obj_b.render(query=query_val, content=content_val)

            config = ABConfig(
                model_a=str(self.query_one("#model-select-a", Select).value),
                prompt_a=rendered_a,
                model_b=str(self.query_one("#model-select-b", Select).value),
                prompt_b=rendered_b,
                use_vault=vault_enabled,
                user_id=user_id
            )

            # 3. Generate & Validate
            if dual_mode:
                result = await ab_engine.run_test("", config) # Query is already in the prompt
                self.current_test_id = result.test_id
                
                # Show results with validation status
                area_a.update(self.format_result(result.result_a, result.validation_a))
                area_b.update(self.format_result(result.result_b, result.validation_b))
                
                # Show voting
                self.query_one("#vote-a").remove_class("hidden")
                self.query_one("#vote-b").remove_class("hidden")
            else:
                from src.orchestration.generator import generator
                res = await generator.generate(config.model_a, f"{config.prompt_a}\n\n{text_to_process}")
                
                # Manual validation pass for single mode if vault enabled
                report = None
                if vault_enabled:
                    context = vault_service.get_vault_context(user_id)
                    report = await guardrail_service.validate_output(query_val, res.response, context)
                
                area_a.update(self.format_result(res, report))

            self.update_audit_log()

        except Exception as e:
            area_a.update(f"[red]Error: {str(e)}[/red]")
            logger.exception("Error in process_request")

    def format_result(self, res, report: Optional[ValidationReport] = None) -> str:
        if not res.success:
            return f"[red]Generation Failed: {res.error}[/red]"
        
        status_line = ""
        if report:
            if not report.is_safe:
                status_line = f"[bold white on red] HALLUCINATION WARNING: {report.reason} [/bold white on red]\n\n"
            else:
                status_line = "[bold green]✓ Verified against Vault[/bold green]\n\n"

        metrics = f"[dim]Latency: {res.latency_ms}ms | Tokens/sec: {res.tokens_per_sec}[/dim]"
        return f"{status_line}{metrics}\n\n{res.response}"

    @on(Button.Pressed, "#vote-a")
    def vote_a(self) -> None:
        self.record_vote(0)

    @on(Button.Pressed, "#vote-b")
    def vote_b(self) -> None:
        self.record_vote(1)

    def record_vote(self, index: int) -> None:
        if self.current_test_id:
            ab_engine.record_preference(self.current_test_id, index, user_id=self.app.user_session.user_id)
            self.query_one("#vote-a").add_class("hidden")
            self.query_one("#vote-b").add_class("hidden")
            self.query_one("#chat-area-a", Static).update("[green]Preference recorded![/green]\n\n" + self.query_one("#chat-area-a", Static).renderable)
            self.update_audit_log()

class SecureAssistantApp(App):
    """The main Textual application."""
    user_session = None
    
    CSS = """
    #login-container {
        width: 40;
        height: 20;
        border: thick $primary;
        padding: 1;
        align: center middle;
    }
    #login-title {
        text-align: center;
        margin-bottom: 1;
        text-style: bold;
    }
    .sub-title {
        margin-top: 1;
        text-style: italic;
        color: $accent;
    }
    .toggle-row {
        height: auto;
        margin-top: 0;
        margin-bottom: 0;
    }
    .toggle-row Static {
        width: 1fr;
    }
    #ingest-bar {
        height: auto;
        margin-bottom: 1;
    }
    #vote-bar {
        height: auto;
        align: center middle;
        margin-bottom: 1;
    }
    #vote-bar Button {
        margin: 0 2;
    }
    #file-input {
        width: 1fr;
    }
    #error-msg {
        text-align: center;
        margin-top: 1;
    }
    #left-pane {
        width: 60%;
        border: solid $accent;
        padding: 1;
    }
    #right-pane {
        width: 40%;
        border: solid $accent;
        padding: 1;
    }
    .pane-title {
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #chat-container {
        height: 1fr;
        border: solid $surface;
        margin-bottom: 1;
    }
    #chat-container.side-by-side {
        layout: horizontal;
    }
    #pane-a, #pane-b {
        height: 1fr;
        padding: 1;
        overflow: auto;
    }
    #chat-container.side-by-side #pane-a {
        width: 50%;
        border-right: vkey $surface;
    }
    #chat-container.side-by-side #pane-b {
        width: 50%;
    }
    #audit-table {
        height: 10;
    }
    .metric-box {
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
        height: auto;
    }
    .sparkline {
        height: 1;
        color: $success;
    }
    .hidden {
        display: none;
    }
    """

    def on_mount(self) -> None:
        prompt_watcher.start()
        self.push_screen(LoginScreen())

    def on_unmount(self) -> None:
        prompt_watcher.stop()

if __name__ == "__main__":
    app = SecureAssistantApp()
    app.run()
