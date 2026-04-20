import "@testing-library/jest-native/extend-expect";

jest.mock("@react-native-async-storage/async-storage", () => {
	let storage: Record<string, string> = {};

	return {
		__esModule: true,
		default: {
			setItem: jest.fn(async (key: string, value: string) => {
				storage[key] = value;
			}),
			getItem: jest.fn(async (key: string) => storage[key] ?? null),
			removeItem: jest.fn(async (key: string) => {
				delete storage[key];
			}),
			clear: jest.fn(async () => {
				storage = {};
			}),
			getAllKeys: jest.fn(async () => Object.keys(storage)),
			multiSet: jest.fn(async (entries: [string, string][]) => {
				for (const [key, value] of entries) {
					storage[key] = value;
				}
			}),
			multiGet: jest.fn(async (keys: string[]) => keys.map((key) => [key, storage[key] ?? null])),
			multiRemove: jest.fn(async (keys: string[]) => {
				for (const key of keys) {
					delete storage[key];
				}
			}),
		},
	};
});
