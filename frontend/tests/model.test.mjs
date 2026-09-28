import assert from 'node:assert/strict';
import test from 'node:test';
import {matchProvider, suggestAlias} from '../src/model.ts';
import {copy, errors, errorText} from '../src/i18n.ts';
const providers = {gmail:{domains:['gmail.com']}, custom:{domains:[]}, outlook:{domains:['outlook.com']}};
test('domain matching cannot route custom or lookalike addresses to preset servers', () => {
  assert.equal(matchProvider('User@GMAIL.COM', providers), 'gmail');
  for (const value of ['user@gmail.com.evil.test', 'user@notgmail.com', 'user@mail.gmail.com', 'user@company.test', 'user@@gmail.com']) assert.equal(matchProvider(value, providers), 'custom');
  assert.equal(matchProvider('user@outlook.com', providers), 'outlook');
});
test('aliases handle non-Latin local parts, punctuation and collisions', () => {
  assert.equal(suggestAlias('123@qq.com', ['mail', 'mail-2']), 'mail-3');
  assert.equal(suggestAlias('测试@example.test', []), 'mail');
  assert.match(suggestAlias('user.name+tag@example.test', ['user-name-tag']), /^[a-z][a-z0-9-]{0,39}$/);
});
test('both languages have complete copy, matching placeholders and no mixed-language errors', () => {
  const zh=copy('zh'), en=copy('en');
  for (const key of Object.keys(zh)) {
    assert.ok(zh[key] && en[key], key);
    assert.doesNotMatch(en[key], /[\u4e00-\u9fff]/, key);
    assert.deepEqual(zh[key].match(/\{\w+\}/g), en[key].match(/\{\w+\}/g), key);
  }
  for (const code of Object.keys(errors)) {
    assert.ok(errorText(code,'zh'));
    assert.doesNotMatch(errorText(code,'en'), /[\u4e00-\u9fff]/, code);
  }
  assert.equal(errorText('UNKNOWN RAW SECRET', 'en'), errorText('operation_failed','en'));
});
