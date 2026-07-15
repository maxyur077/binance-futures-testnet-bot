document.addEventListener("DOMContentLoaded", () => {
    const state = {
        side: "BUY",
        gridSide: "BUY",
        orders: [],
    };

    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const API_BASE = "/api";

    function checkHealth() {
        fetch(`${API_BASE}/health`)
            .then((r) => r.json())
            .then((data) => {
                const healthDot = $("#health-dot");
                const healthText = $("#health-text");
                const healthIndicator = $("#health-indicator");
                if (data.status === "healthy") {
                    healthDot.className = "w-2 h-2 rounded-full bg-accent-buy shadow-[0_0_8px_rgba(14,203,129,0.5)]";
                    healthText.textContent = "Connected";
                    healthIndicator.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-buy/10 border border-accent-buy/20";
                    $("#disconnect-btn").classList.remove("hidden");
                    $("#connection-btn").classList.add("hidden");
                } else {
                    throw new Error("Unhealthy");
                }
            })
            .catch(() => {
                const healthDot = $("#health-dot");
                const healthText = $("#health-text");
                const healthIndicator = $("#health-indicator");
                healthDot.className = "w-2 h-2 rounded-full bg-accent-sell shadow-[0_0_8px_rgba(246,70,93,0.5)]";
                healthText.textContent = "Disconnected";
                healthIndicator.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-sell/10 border border-accent-sell/20";
                $("#disconnect-btn").classList.add("hidden");
                $("#connection-btn").classList.remove("hidden");
            });
    }

    checkHealth();
    setInterval(checkHealth, 30000);

    $$(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            $$(".tab-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            $$(".tab-panel").forEach((p) => p.classList.add("hidden"));
            $(`#panel-${btn.dataset.tab}`).classList.remove("hidden");
        });
    });

    function setupSideButtons(buyId, sellId, callback) {
        const buyBtn = $(buyId);
        const sellBtn = $(sellId);

        buyBtn.addEventListener("click", () => {
            buyBtn.classList.add("active");
            sellBtn.classList.remove("active");
            callback("BUY");
        });

        sellBtn.addEventListener("click", () => {
            sellBtn.classList.add("active");
            buyBtn.classList.remove("active");
            callback("SELL");
        });
    }

    function updateSubmitButton() {
        const btn = $("#submit-btn");
        const orderType = $("#order-type").value;
        if (state.side === "BUY") {
            btn.className = "w-full py-3.5 rounded-xl text-sm font-bold transition-all duration-300 submit-buy";
            btn.textContent = `Place BUY ${orderType} Order`;
        } else {
            btn.className = "w-full py-3.5 rounded-xl text-sm font-bold transition-all duration-300 submit-sell";
            btn.textContent = `Place SELL ${orderType} Order`;
        }
    }

    function updateGridSubmitButton() {
        const btn = $("#grid-submit-btn");
        if (state.gridSide === "BUY") {
            btn.className = "w-full py-3.5 rounded-xl text-sm font-bold transition-all duration-300 submit-buy";
            btn.textContent = "Execute BUY Grid Strategy";
        } else {
            btn.className = "w-full py-3.5 rounded-xl text-sm font-bold transition-all duration-300 submit-sell";
            btn.textContent = "Execute SELL Grid Strategy";
        }
    }

    setupSideButtons("#btn-buy", "#btn-sell", (side) => {
        state.side = side;
        updateSubmitButton();
    });

    setupSideButtons("#grid-btn-buy", "#grid-btn-sell", (side) => {
        state.gridSide = side;
        updateGridSubmitButton();
    });

    $("#order-type").addEventListener("change", () => {
        const type = $("#order-type").value;
        const priceGroup = $("#price-group");
        const stopGroup = $("#stop-price-group");

        priceGroup.classList.add("hidden");
        stopGroup.classList.add("hidden");

        if (type === "LIMIT" || type === "STOP") {
            priceGroup.classList.remove("hidden");
        }
        if (type === "STOP_MARKET" || type === "STOP") {
            stopGroup.classList.remove("hidden");
        }

        updateSubmitButton();
    });

    function updateGridPreview() {
        const lower = parseFloat($("#grid-lower").value);
        const upper = parseFloat($("#grid-upper").value);
        const levels = parseInt($("#grid-levels").value);
        const preview = $("#grid-preview");
        const container = $("#grid-levels-preview");

        if (!lower || !upper || !levels || lower >= upper || levels < 2) {
            preview.classList.add("hidden");
            return;
        }

        preview.classList.remove("hidden");
        container.innerHTML = "";

        const step = (upper - lower) / (levels - 1);
        for (let i = 0; i < levels; i++) {
            const price = (lower + i * step).toFixed(2);
            const tag = document.createElement("span");
            tag.className = "grid-level-tag";
            tag.textContent = price;
            container.appendChild(tag);
        }
    }

    ["#grid-lower", "#grid-upper", "#grid-levels"].forEach((sel) => {
        $(sel).addEventListener("input", updateGridPreview);
    });

    function showLoading(text) {
        const overlay = $("#loading-overlay");
        $("#loading-text").textContent = text;
        overlay.classList.remove("hidden");
        overlay.classList.add("active");
    }

    function hideLoading() {
        const overlay = $("#loading-overlay");
        overlay.classList.add("hidden");
        overlay.classList.remove("active");
    }

    function showToast(type, title, message) {
        const container = $("#toast-container");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;

        const icons = {
            success: `<svg class="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>`,
            error: `<svg class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>`,
            info: `<svg class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
        };

        toast.innerHTML = `
            ${icons[type] || icons.info}
            <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-white">${title}</p>
                <p class="text-xs text-gray-400 mt-0.5 break-words">${message}</p>
            </div>
            <button class="text-gray-500 hover:text-white transition-colors flex-shrink-0" onclick="this.closest('.toast').remove()">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
        `;

        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(16px)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    function addOrderToHistory(data, isError) {
        const container = $("#order-history");
        const empty = container.querySelector(".flex.flex-col.items-center");
        if (empty) empty.remove();

        const card = document.createElement("div");
        card.className = `order-card ${isError ? "error" : "success"}`;

        if (isError) {
            card.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-red-400">FAILED</span>
                    <span class="text-[10px] text-gray-600 font-mono">${new Date().toLocaleTimeString()}</span>
                </div>
                <p class="text-xs text-gray-400">${data.detail || data.error || "Unknown error"}</p>
            `;
        } else if (data.totalOrders !== undefined) {
            card.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-green-400">GRID — ${data.totalOrders} orders</span>
                    <span class="text-[10px] text-gray-600 font-mono">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="space-y-1">
                    ${data.orders.map((o, i) => `
                        <div class="flex items-center justify-between text-[11px]">
                            <span class="text-gray-500">#${i + 1}</span>
                            <span class="font-mono text-gray-300">${o.price}</span>
                            <span class="font-mono ${o.side === "BUY" ? "text-green-400" : "text-red-400"}">${o.status}</span>
                        </div>
                    `).join("")}
                </div>
            `;
        } else {
            const sideColor = data.side === "BUY" ? "text-green-400" : "text-red-400";
            card.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-semibold ${sideColor}">${data.side}</span>
                        <span class="text-[10px] text-gray-500 bg-gray-800 px-1.5 py-0.5 rounded">${data.orderType}</span>
                    </div>
                    <span class="text-[10px] text-gray-600 font-mono">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="grid grid-cols-2 gap-y-1.5 text-[11px]">
                    <div>
                        <span class="text-gray-600">Symbol</span>
                        <p class="font-semibold text-white">${data.symbol}</p>
                    </div>
                    <div>
                        <span class="text-gray-600">Order ID</span>
                        <p class="font-mono text-gray-300">${data.orderId}</p>
                    </div>
                    <div>
                        <span class="text-gray-600">Quantity</span>
                        <p class="font-mono text-gray-300">${data.executedQty} / ${data.origQty}</p>
                    </div>
                    <div>
                        <span class="text-gray-600">Avg Price</span>
                        <p class="font-mono text-gray-300">${data.avgPrice}</p>
                    </div>
                    <div class="col-span-2">
                        <span class="text-gray-600">Status</span>
                        <span class="ml-2 text-xs font-semibold ${data.status === "FILLED" || data.status === "NEW" ? "text-green-400" : "text-yellow-400"}">${data.status}</span>
                    </div>
                </div>
            `;
        }

        container.insertBefore(card, container.firstChild);
    }

    $("#order-form").addEventListener("submit", async (e) => {
        e.preventDefault();

        const orderType = $("#order-type").value;
        const payload = {
            symbol: $("#symbol").value,
            side: state.side,
            orderType: orderType,
            quantity: parseFloat($("#quantity").value),
            timeInForce: "GTC",
        };

        if (orderType === "LIMIT" || orderType === "STOP") {
            const price = parseFloat($("#price").value);
            if (!price || price <= 0) {
                showToast("error", "Validation Error", "Price is required for this order type");
                return;
            }
            payload.price = price;
        }

        if (orderType === "STOP_MARKET" || orderType === "STOP") {
            const stopPrice = parseFloat($("#stop-price").value);
            if (!stopPrice || stopPrice <= 0) {
                showToast("error", "Validation Error", "Stop price is required for this order type");
                return;
            }
            payload.stopPrice = stopPrice;
        }

        if (!payload.quantity || payload.quantity <= 0) {
            showToast("error", "Validation Error", "Quantity must be a positive number");
            return;
        }

        showLoading(`Placing ${state.side} ${orderType} order...`);

        try {
            const res = await fetch(`${API_BASE}/orders`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            hideLoading();

            if (data.error) {
                showToast("error", "Order Failed", data.detail);
                addOrderToHistory(data, true);
            } else {
                showToast("success", "Order Placed", `${data.symbol} ${data.side} — ID: ${data.orderId}`);
                addOrderToHistory(data, false);
            }
        } catch (err) {
            hideLoading();
            showToast("error", "Network Error", err.message);
            addOrderToHistory({ detail: err.message }, true);
        }
    });

    $("#grid-form").addEventListener("submit", async (e) => {
        e.preventDefault();

        const payload = {
            symbol: $("#grid-symbol").value,
            side: state.gridSide,
            quantityPerOrder: parseFloat($("#grid-quantity").value),
            lowerPrice: parseFloat($("#grid-lower").value),
            upperPrice: parseFloat($("#grid-upper").value),
            gridLevels: parseInt($("#grid-levels").value),
            timeInForce: "GTC",
        };

        if (!payload.quantityPerOrder || payload.quantityPerOrder <= 0) {
            showToast("error", "Validation Error", "Quantity must be positive");
            return;
        }
        if (!payload.lowerPrice || !payload.upperPrice || payload.lowerPrice >= payload.upperPrice) {
            showToast("error", "Validation Error", "Lower price must be less than upper price");
            return;
        }
        if (!payload.gridLevels || payload.gridLevels < 2 || payload.gridLevels > 50) {
            showToast("error", "Validation Error", "Grid levels must be between 2 and 50");
            return;
        }

        showLoading(`Executing grid strategy — ${payload.gridLevels} orders...`);

        try {
            const res = await fetch(`${API_BASE}/orders/grid`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            hideLoading();

            if (data.error) {
                showToast("error", "Grid Failed", data.detail);
                addOrderToHistory(data, true);
            } else {
                showToast("success", "Grid Executed", `${data.totalOrders} orders placed successfully`);
                addOrderToHistory(data, false);
            }
        } catch (err) {
            hideLoading();
            showToast("error", "Network Error", err.message);
            addOrderToHistory({ detail: err.message }, true);
        }
    });

    $("#clear-history").addEventListener("click", () => {
        const container = $("#order-history");
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-12 text-gray-500">
                <svg class="w-12 h-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p class="text-sm">No orders yet</p>
                <p class="text-xs text-gray-600 mt-1">Place an order to see results here</p>
            </div>
        `;
        showToast("info", "Cleared", "Order history cleared");
    });

    // Connection Modal
    const connectionModal = $("#connection-modal");
    $("#connection-btn").addEventListener("click", () => connectionModal.classList.remove("hidden", "items-center", "justify-center"));
    $("#connection-btn").addEventListener("click", () => {
        connectionModal.classList.remove("hidden");
        connectionModal.classList.add("flex");
    });
    $("#close-connection-modal").addEventListener("click", () => {
        connectionModal.classList.add("hidden");
        connectionModal.classList.remove("flex");
    });

    $("#connection-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const apiKey = $("#api-key").value;
        const apiSecret = $("#api-secret").value;
        
        try {
            const res = await fetch(`${API_BASE}/connections`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ api_key: apiKey, api_secret: apiSecret, name: "default" })
            });
            if (res.ok) {
                showToast("success", "Connection Saved", "API credentials saved successfully");
                connectionModal.classList.add("hidden");
                connectionModal.classList.remove("flex");
                checkHealth();
            } else {
                showToast("error", "Error", "Failed to save connection");
            }
        } catch (err) {
            showToast("error", "Network Error", err.message);
        }
    });

    $("#disconnect-btn").addEventListener("click", async () => {
        try {
            const res = await fetch(`${API_BASE}/connections/active`, {
                method: "DELETE"
            });
            if (res.ok) {
                $("#api-key").value = "";
                $("#api-secret").value = "";
                showToast("info", "Disconnected", "API keys removed from database");
                checkHealth();
            } else {
                showToast("error", "Error", "Failed to disconnect");
            }
        } catch (err) {
            showToast("error", "Network Error", err.message);
        }
    });

    // Symbol Search
    function setupSymbolSearch(inputId, dropdownId) {
        const input = $(inputId);
        const dropdown = $(dropdownId);
        let debounceTimer;

        input.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            const q = input.value.trim();
            if (q.length === 0) {
                dropdown.classList.add("hidden");
                return;
            }
            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`${API_BASE}/symbols?q=${q}`);
                    const symbols = await res.json();
                    
                    if (symbols.length > 0) {
                        dropdown.innerHTML = symbols.map(s => `
                            <div class="px-4 py-2 hover:bg-surface-300 cursor-pointer text-sm text-white symbol-option" data-symbol="${s.symbol}">
                                ${s.symbol} <span class="text-xs text-gray-500 ml-2">${s.base_asset}/${s.quote_asset}</span>
                            </div>
                        `).join("");
                        dropdown.classList.remove("hidden");
                    } else {
                        dropdown.innerHTML = `<div class="px-4 py-2 text-sm text-gray-500">No symbols found</div>`;
                        dropdown.classList.remove("hidden");
                    }
                } catch (err) {
                    console.error("Failed to fetch symbols", err);
                }
            }, 300);
        });

        dropdown.addEventListener("click", (e) => {
            const option = e.target.closest(".symbol-option");
            if (option) {
                input.value = option.dataset.symbol;
                dropdown.classList.add("hidden");
            }
        });

        document.addEventListener("click", (e) => {
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add("hidden");
            }
        });
    }

    setupSymbolSearch("#symbol", "#symbol-dropdown");
    setupSymbolSearch("#grid-symbol", "#grid-symbol-dropdown");

    updateSubmitButton();
    updateGridSubmitButton();
});
