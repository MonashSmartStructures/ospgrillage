# Contributing to ospgrillage

We warmly welcome contributions to *ospgrillage* and hope to create an active community of bridge engineers (both practicing and researching) interested in using and contributing to this software.

If you wish to discuss a potential contribution, please raise an issue and we can talk it through.

For the benefit of the community, we have a [code of conduct]() and ask everyone to follow it in interactions with the project.

## Code of conduct

Please read and follow our [Code of Conduct](https://github.com/MonashSmartStructures/ospgrillage/blob/main/.github/CODE_OF_CONDUCT.md).

## Questions or Problems

Please [submit an issue](#submit-issue) to *ospgrillage*'s repository.

## Bug reports

If you think you have identified a bug in the source code, you can help us by [submitting an issue](#submit-issue) to *ospgrillage* repository.
If you have a fix for bugs, you can [submit a Pull Request](#submit-pr) for it.


## Contributing improvements
We'd love to hear your ideas on new features or improvements to *ospgrillage*. If you like to implement a new feature, please [submit an issue](https://github.com/MonashSmartStructures/ospgrillage/issues) on this. First outline your proposal so that it can be discussed. This allow us to better coordinate our efforts, prevent duplication of work, and provide feedback on your ideas of features.


## Commit Message Format

### Background
*ospgrillage* adopts a specific semantic commit message format called [Conventional Commits](https://www.conventionalcommits.org) that allows us to automate change logs and otherwise categorize efforts. You can read more about this at [Angular](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit) and [here](https://nitayneeman.com/posts/understanding-semantic-commit-messages-using-git-and-angular/).

Because of the benefits that the semantic commit message format brings, we will enforce this format on all commits. 

### Format
The commit message requires a mandatory `header` with an optional `body` and `footer`:

```bash
<header>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

#### Header

The `header` is mandatory and must conform to the following format: 

```bash
<type>(<scope>): <short summary>
```

where `<type>` must be one of the following:

* **build** : Changes affecting build system
* **docs**: Changes to documentation only
* **ci**: Changes to continuous integration scripts or system
* **feat**: Change/add new feature
* **fix**: Bug fixing
* **perf**: Changes related to package performance
* **refactor**: Changes other than bug fixes or features
* **test**: Addition/modification to tests

`<scope>` is optional information that indicates the context of the change.

`<short summary>` provides a very brief description of change. 

* use present tense: e.g. "change" not "changed"
* no dot (.) at end
* first letter lowercase

#### Body (Optional)

The optional `<body>` should contain explanation for the change in commit message. For example, explaining *why* the changes is being made.

Similar to `<short summary>` use the imperative, present tense: e.g. "fix" but not "fixed" nor "fixing".

#### Footer (Optional)

The `<footer>` is an optional line that explains any significant consequences of the change, such as a breaking change, closing a PR, and so on.

### Practical Example

Using the command line interface for git, an example is:

```bash
git commit -m "feat(elements): added the nonlinearBeamColumn" -m "Per the outstanding task list, this commit adds the outstanding element to enable a nonlinear analysis of the bridge deck." -m "Issue #5"
```

Notice that the header, footer, and body are concatenated using the `-m` arguments.
