import dynamoose from 'dynamoose';
import { Item } from 'dynamoose/dist/Item';
import { STREAMS_TABLE, StreamSchema } from './schema';

export class Stream extends Item {
    streamId!: string;
    chatId!: string;
    createdAt!: string;
}

export const StreamModel = dynamoose.model<Stream>(STREAMS_TABLE, StreamSchema);
