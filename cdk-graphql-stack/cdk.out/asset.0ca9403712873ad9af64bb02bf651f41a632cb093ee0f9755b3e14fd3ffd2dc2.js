export function request(ctx) {
  const { limit = 40, nextToken } = ctx.args;
  return ddb.scan({ limit, nextToken });
}

export function response(ctx) {
  console.log(`response is ${ctx.result}`);
  const res = JSON.parse(ctx.result.body);

  return { items: res };
}
