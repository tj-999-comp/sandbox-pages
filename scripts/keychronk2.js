(() => {
	const DEFAULT_SWITCH_IMAGE = new URL("../images/switch-placeholder.svg", window.location.href).href;

	const SWITCH_CATALOG = {
		"sw-01": { name: "Gateron Smoothie Switch Set", type: "Linear / 40+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/files/e3842803a3_800x.jpg?v=1711087333" },
		"sw-02": { name: "Durock Full POK Mocha Silk", type: "Linear / 48g", image: "https://shop.yushakobo.jp/cdn/shop/files/He4b418acab144519a29482e72d5cf711J_800x.webp?v=1739008628" },
		"sw-03": { name: "Gateron Oil King (V2)", type: "Linear / 不明", image: "https://shop.yushakobo.jp/cdn/shop/products/2_0b379e4c-a4b1-48fd-8021-e31ac62983a3_800x.jpg?v=1649307760" },
		"sw-04": { name: "WS Pearl Switch", type: "Linear / 不明", image: "https://m.media-amazon.com/images/I/51NqamC721L._SL1500_.jpg" },
		"sw-05": { name: "80Retros X HMX Joker", type: "Linear / 40+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/files/JOKER5_400x.webp?v=1731468266" },
		"sw-06": { name: "Gateron Mini i", type: "Tactile / 50+10gf", image: "https://shop.yushakobo.jp/cdn/shop/files/d874824108_800x.webp?v=1696935274" },
		"sw-07": { name: "TTC Frozen Silent V2", type: "Silent Linear / 39gf", image: "https://shop.yushakobo.jp/cdn/shop/files/switch_6edaa168-6eed-4772-8e70-f51a9dcf9ba3_800x.jpg?v=1742539914" },
		"sw-08": { name: "Kailh Midnight Silent V2", type: "Silent Linear / 40+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/products/11-A_800x.jpg?v=1692087096" },
		"sw-09": { name: "Kailh Yushakobo Fairy Silent", type: "Silent Linear / 35+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/products/IMG_20230125_183904_800x.png?v=1691659231" },
		"sw-10": { name: "Durock Silent Linear Dolphin", type: "Silent Linear / 62gf", image: "https://shop.yushakobo.jp/cdn/shop/products/P3141786_800x.jpg?v=1647198384" },
		"sw-11": { name: "Kailh Deep Sea Silent Pro Box", type: "Silent Linear / 45+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/files/Kailh-Deep-Sea-Silent-Pro-Box-Red-Switch_800x.webp?v=1733460884" },
		"sw-12": { name: "Outemu Lemon Switch V3", type: "Silent Tactile / 35+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/files/IMG_20250112_105335_3_13ef134e-d5ed-434d-b7a5-aad6059d0dde_800x.jpg?v=1736647508" },
		"sw-13": { name: "TTC Bluish White Silent", type: "Silent Tactile / 42+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/files/ttc-silent-bluish-whitebluish-white-switches-mechkeysshop-897452_800x.webp?v=1733462585" },
		"sw-14": { name: "Durock T1 Shrimp", type: "Silent Tactile / 不明", image: "https://shop.yushakobo.jp/cdn/shop/products/3-A_800x.jpg?v=1657446237" },
		"sw-15": { name: "Outemu Creamy Yellow", type: "Silent Tactile / 45gf", image: "https://shop.yushakobo.jp/cdn/shop/files/DSCF9608_800x.jpg?v=1755502181" },
		"sw-16": { name: "Kailh Midnight Silent V2 Tactile", type: "Silent Tactile / 55+-10gf", image: "https://shop.yushakobo.jp/cdn/shop/products/kailh-midnight-slient-tactile-switch-pro01094981273_700x.webp?v=1656917770" },
		"sw-17": { name: "Gateron G Pro 3.0 Red", type: "Linear / 45+-15gf", image: "https://shop.yushakobo.jp/cdn/shop/files/20230520-916_700x.jpg?v=1685254435" }
	};

	const keyElements = document.querySelectorAll(".key[data-key]");
	if (!keyElements.length) {
		return;
	}

	const currentKeyElement = document.getElementById("current-key");
	const switchKeyLabelElement = document.getElementById("switch-key-label");
	const switchClassLabelElement = document.getElementById("switch-class-label");
	const switchNameLabelElement = document.getElementById("switch-name-label");
	const switchTypeLabelElement = document.getElementById("switch-type-label");
	const switchImageElement = document.getElementById("switch-image");
	const keyMap = new Map();
	const comboMap = new Map();

	if (switchImageElement) {
		switchImageElement.src = DEFAULT_SWITCH_IMAGE;
	}

	const setSwitchImage = (imageUrl) => {
		if (!switchImageElement) {
			return;
		}

		if (!imageUrl) {
			switchImageElement.src = DEFAULT_SWITCH_IMAGE;
			return;
		}

		switchImageElement.onerror = () => {
			switchImageElement.src = DEFAULT_SWITCH_IMAGE;
		};
		switchImageElement.src = imageUrl;
	};

	keyElements.forEach((element) => {
		const key = element.getAttribute("data-key");
		const code = element.getAttribute("data-code");
		const combo = element.getAttribute("data-combo");
		const identifiers = [key, code].filter(Boolean);

		if (!identifiers.length) {
			if (!combo) {
				return;
			}
		}

		identifiers.forEach((identifier) => {
			const elements = keyMap.get(identifier) ?? [];
			elements.push(element);
			keyMap.set(identifier, elements);
		});

		if (combo) {
			const comboElements = comboMap.get(combo) ?? [];
			comboElements.push(element);
			comboMap.set(combo, comboElements);
		}
	});

	const clearAllHighlights = () => {
		keyElements.forEach((element) => {
			element.classList.remove("active");
		});
	};

	const setCurrentKeyText = (text) => {
		if (!currentKeyElement) {
			return;
		}
		currentKeyElement.textContent = text;
	};

	const findSwitchClass = (element) => {
		const matchedClass = [...element.classList].find((className) => /^sw-\d+$/i.test(className));
		if (!matchedClass) {
			return "";
		}

		const normalizedNumber = Number.parseInt(matchedClass.replace(/[^\d]/g, ""), 10);
		if (!Number.isInteger(normalizedNumber)) {
			return "";
		}

		return `sw-${String(normalizedNumber).padStart(2, "0")}`;
	};

	const setSwitchInfo = (element, pressedLabel) => {
		if (!switchKeyLabelElement || !switchClassLabelElement || !switchNameLabelElement || !switchTypeLabelElement) {
			return;
		}

		switchKeyLabelElement.textContent = pressedLabel;

		if (!element) {
			switchClassLabelElement.textContent = "未設定";
			switchNameLabelElement.textContent = "未設定";
			switchTypeLabelElement.textContent = "未設定";
			setSwitchImage("");
			return;
		}

		const switchClass = findSwitchClass(element);
		if (!switchClass) {
			switchClassLabelElement.textContent = "未設定";
			switchNameLabelElement.textContent = "未設定";
			switchTypeLabelElement.textContent = "未設定";
			setSwitchImage("");
			return;
		}

		const switchInfo = SWITCH_CATALOG[switchClass];
		switchClassLabelElement.textContent = switchClass;
		switchNameLabelElement.textContent = switchInfo?.name ?? "カタログ未登録";
		switchTypeLabelElement.textContent = switchInfo?.type ?? "カタログ未登録";

		setSwitchImage(switchInfo?.image ?? "");
	};

	const buildComboLabel = (event) => {
		const modifiers = [];

		if (event.metaKey) {
			modifiers.push("Meta");
		}
		if (event.ctrlKey) {
			modifiers.push("Control");
		}
		if (event.altKey) {
			modifiers.push("Alt");
		}
		if (event.shiftKey && event.code !== "ShiftLeft" && event.code !== "ShiftRight") {
			modifiers.push("Shift");
		}

		if (!modifiers.length) {
			return "";
		}

		return `${modifiers.join("+")}+${event.code}`;
	};

	const highlightElements = (elements, label) => {
		clearAllHighlights();
		elements.forEach((element) => {
			element.classList.add("active");
		});
		setCurrentKeyText(label);
		setSwitchInfo(elements[0], label);
	};

	const activateByCode = (code, keyLabel) => {
		const matchedElements = keyMap.get(code) ?? [];
		if (!matchedElements.length) {
			setCurrentKeyText(`未対応キー (${keyLabel})`);
			setSwitchInfo(undefined, `${keyLabel} [${code}]`);
			return;
		}

		highlightElements(matchedElements, `${keyLabel} [${code}]`);
	};

	window.addEventListener("keydown", (event) => {
		const comboLabel = buildComboLabel(event);
		const comboElements = comboLabel ? comboMap.get(comboLabel) ?? [] : [];

		if (comboElements.length || keyMap.has(event.code) || keyMap.has(event.key)) {
			event.preventDefault();
		}

		if (comboElements.length) {
			const keyLabel = comboElements[0].getAttribute("data-key") ?? comboLabel;
			highlightElements(comboElements, keyLabel);
			return;
		}

		activateByCode(event.code, event.key);
	}, { capture: true });
})();