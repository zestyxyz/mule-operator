export function CreateJoinMessage(name, type, room)
{
    return {
        name: name,
        room: room,
        type: type,
    };
}