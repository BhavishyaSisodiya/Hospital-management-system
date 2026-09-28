import api from "./axios";

export async function sendChatMessage(messages) {
    const { data } = await api.post("/chat/", {
        messages: messages.map(({ role, content }) => ({
            role,
            content,
        })),
    });
    return data;
}