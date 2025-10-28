import dynamoose from 'dynamoose';
import { Item } from 'dynamoose/dist/Item';
import { SUGGESTIONS_TABLE, SuggestionSchema } from './schema';

export class Suggestion extends Item {
    suggestionId!: string;
    documentId!: string;
    documentCreatedAt!: string;
    originalText!: string;
    suggestedText!: string;
    description?: string;
    isResolved!: boolean;
    userId!: string;
    createdAt!: string;
}

export const SuggestionModel = dynamoose.model<Suggestion>(SUGGESTIONS_TABLE, SuggestionSchema);
