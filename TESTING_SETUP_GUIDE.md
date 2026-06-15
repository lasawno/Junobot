# Testing Setup Guide for Junobot

## Quick Start Checklist

- [ ] Install testing dependencies
- [ ] Configure Jest or testing framework
- [ ] Set up test file structure
- [ ] Add pre-commit hooks for tests
- [ ] Configure CI/CD to run tests
- [ ] Set up code coverage reporting
- [ ] Create test utilities and helpers
- [ ] Document project-specific test patterns

## Step-by-Step Setup

### 1. Install Testing Framework

```bash
npm install --save-dev jest ts-jest @types/jest
npm install --save-dev discord.js-mock nock sinon
```

### 2. Configure Jest (jest.config.js)

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/index.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
};
```

### 3. Set Up Test Directory Structure

```
Junobot/
├── src/
│   ├── commands/
│   ├── events/
│   ├── utils/
│   └── index.ts
├── tests/
│   ├── unit/
│   │   ├── commands/
│   │   ├── events/
│   │   └── utils/
│   ├── integration/
│   │   ├── commands/
│   │   └── events/
│   ├── e2e/
│   └── fixtures/
│       ├── mockData.ts
│       ├── mockClient.ts
│       └── mockGuild.ts
├── jest.config.js
└── package.json
```

### 4. Add NPM Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:coverage:html": "jest --coverage && open coverage/index.html",
    "test:ci": "jest --coverage --ci --maxWorkers=2"
  }
}
```

### 5. Create Test Fixtures/Mocks

**tests/fixtures/mockClient.ts**
```typescript
import { Client, Collection } from 'discord.js';

export function createMockClient(): Partial<Client> {
  return {
    commands: new Collection(),
    user: {
      id: '123456789',
      username: 'TestBot',
      bot: true,
    },
  };
}
```

**tests/fixtures/mockGuild.ts**
```typescript
export function createMockGuild() {
  return {
    id: '111111111',
    name: 'Test Guild',
    ownerId: '222222222',
    members: {
      fetch: jest.fn().mockResolvedValue({
        id: '333333333',
        user: { username: 'TestUser' },
      }),
    },
  };
}
```

### 6. Example Test Template

**tests/unit/utils/validation.test.ts**
```typescript
import { validateCommand, ValidationError } from '../../../src/utils/validation';

describe('Validation Utils', () => {
  describe('validateCommand', () => {
    it('should validate correct command format', () => {
      const result = validateCommand('!help');
      expect(result.isValid).toBe(true);
    });

    it('should reject invalid prefix', () => {
      const result = validateCommand('?help');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('Invalid prefix');
    });

    it('should handle empty command', () => {
      const result = validateCommand('');
      expect(result.isValid).toBe(false);
    });

    it('should parse command arguments correctly', () => {
      const result = validateCommand('!say hello world');
      expect(result.command).toBe('say');
      expect(result.args).toEqual(['hello', 'world']);
    });
  });
});
```

### 7. Git Hooks (Pre-commit)

Install husky:
```bash
npm install --save-dev husky
npx husky install
npx husky add .husky/pre-commit "npm run test -- --onlyChanged"
```

### 8. CI/CD Integration (GitHub Actions Example)

**.github/workflows/test.yml**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm run test:ci
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

## Testing Patterns Specific to Discord Bots

### Pattern 1: Testing Command Handlers

```typescript
describe('PingCommand', () => {
  let mockInteraction: any;
  let command: PingCommand;

  beforeEach(() => {
    command = new PingCommand();
    mockInteraction = {
      reply: jest.fn().mockResolvedValue(undefined),
      user: { id: '123' },
      guild: { id: '456' },
    };
  });

  it('should reply with pong', async () => {
    await command.execute(mockInteraction);
    expect(mockInteraction.reply).toHaveBeenCalledWith('Pong!');
  });

  it('should measure latency', async () => {
    await command.execute(mockInteraction);
    const reply = mockInteraction.reply.mock.calls[0][0];
    expect(reply).toMatch(/\d+ms/);
  });
});
```

### Pattern 2: Testing Event Handlers

```typescript
describe('MessageCreate Event', () => {
  let mockClient: any;
  let mockMessage: any;
  let handler: MessageCreateHandler;

  beforeEach(() => {
    mockClient = createMockClient();
    handler = new MessageCreateHandler();
    mockMessage = {
      author: { bot: false, id: '123' },
      guild: createMockGuild(),
      content: '!help',
      reply: jest.fn().mockResolvedValue(undefined),
    };
  });

  it('should ignore bot messages', async () => {
    mockMessage.author.bot = true;
    await handler.handle(mockMessage);
    expect(mockMessage.reply).not.toHaveBeenCalled();
  });

  it('should process valid commands', async () => {
    await handler.handle(mockMessage);
    expect(mockMessage.reply).toHaveBeenCalled();
  });

  it('should handle command errors gracefully', async () => {
    mockMessage.reply.mockRejectedValue(new Error('API Error'));
    await expect(handler.handle(mockMessage)).resolves.not.toThrow();
  });
});
```

### Pattern 3: Testing Async Operations

```typescript
describe('DatabaseService', () => {
  let service: DatabaseService;
  let mockDb: any;

  beforeEach(() => {
    mockDb = {
      query: jest.fn(),
    };
    service = new DatabaseService(mockDb);
  });

  it('should timeout on slow queries', async () => {
    mockDb.query.mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 5000))
    );
    
    const promise = service.getUser('123');
    jest.runAllTimers();
    
    await expect(promise).rejects.toThrow('Query timeout');
  });

  it('should retry on transient errors', async () => {
    mockDb.query
      .mockRejectedValueOnce(new Error('Connection lost'))
      .mockResolvedValueOnce({ id: '123', name: 'User' });
    
    const result = await service.getUser('123');
    expect(result.id).toBe('123');
    expect(mockDb.query).toHaveBeenCalledTimes(2);
  });
});
```

## Coverage Improvement Workflow

1. **Run Coverage Report**
   ```bash
   npm run test:coverage
   ```

2. **Identify Gaps** (files < 80% coverage)
3. **Prioritize** (by risk/criticality)
4. **Add Tests** for missing scenarios
5. **Review** with team
6. **Repeat** monthly

## Resources & Learning

- [Jest Documentation](https://jestjs.io/)
- [Discord.js Documentation](https://discord.js.org/)
- [Testing Best Practices](https://testingjavascript.com/)
- [Jest Cheat Sheet](https://devhints.io/jest)

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tests timing out | Increase timeout: `jest.setTimeout(10000)` |
| Discord API calls fail | Use nock to mock HTTP requests |
| Async tests flaky | Use `done()` callback or return promises |
| Coverage not accurate | Ensure all code paths are exercised |
| Slow test suite | Run tests in parallel, mock heavy operations |

