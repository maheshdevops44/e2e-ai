import dynamoose from 'dynamoose';
import { Item } from 'dynamoose/dist/Item';
import { DOCUMENTS_TABLE, DocumentSchema } from './schema';
import type { ArtifactKind } from '@/components/artifact';

export class Document extends Item {
    documentId!: string;
    userId!: string;
    title!: string;
    content?: string;
    kind!: ArtifactKind;
    createdAt!: string;
}

export const DocumentModel = dynamoose.model<Document>(DOCUMENTS_TABLE, DocumentSchema);
